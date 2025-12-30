import logging
from typing import List
from langchain_community.docstore.document import Document
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, ListItem, Table, Element

from proposal.indexing.constants import WEIGHTED_PROPOSAL_KEYWORDS, PROPOSAL_RELEVANCE_THRESHOLD


LOGGER = logging.getLogger(__name__)


class Stage:

    def run(self):
        raise NotImplementedError


class ProposalRelevanceCheck(Stage):

    """
    This stage evaluates the relevance of a proposal document based on the presence of key sections and overall structure.
    It assigns scores based on weighted keywords and structural elements like titles, lists, and tables.
    If the total score exceeds a predefined threshold, the document is considered relevant.
    """

    def __init__(self, elements: List[Element]):
        super().__init__()
        self.elements = elements
    
    def run(self) -> List[Element]:
        LOGGER.info("Starting Proposal Relevance Check")

        keyword_score, structure_score = 0, 0

        full_text: str = " ".join(e.text.lower() for e in self.elements if e.text)

        LOGGER.info(f"Full text for relevance check length: {len(full_text)}")

        if "request for proposal" in full_text:  # Quick check for RFP presence
            LOGGER.info("Detected 'request for proposal' in document; marking as irrelevant.")
            return []

        for keyword, weight in WEIGHTED_PROPOSAL_KEYWORDS.items():
            keyword_score += full_text.count(keyword) * weight
        
        LOGGER.info(f"Keyword score: {keyword_score}")

        title_count = sum(1 for e in self.elements if isinstance(e, Title))
        list_count = sum(1 for e in self.elements if isinstance(e, ListItem))
        table = sum(1 for e in self.elements if isinstance(e, Table))

        LOGGER.info(f"Title count: {title_count}, List count: {list_count}, Table count: {table}")

        if title_count > 5:
            structure_score += 3
        if list_count / max(len(self.elements), 1) > 0.2:  # Check if more than 20% are lists
            structure_score += 2
        if table > 0:
            structure_score += 2

        LOGGER.info(f"Structure score: {structure_score}")
        LOGGER.info(f"Total score: {keyword_score + structure_score}")
        LOGGER.info("Completed Proposal Relevance Check")
        return self.elements if (keyword_score + structure_score) > PROPOSAL_RELEVANCE_THRESHOLD else []


class DocumentChunker(Stage):

    """
    This stage segments a document into smaller, manageable chunks based on headings.
    Each chunk is created from the text elements that follow a heading until the next heading.
    The chunks are limited to a maximum of 400 words to ensure they are concise and focused.
    Each chunk is stored as a Document with metadata including the original heading and page range.
    """

    def __init__(self, elements: List[Element]):
        super().__init__()
        self.elements = elements
    
    def __build_chunk(self, heading: str, elements: List[Element], page_start: int, page_end: int):
        text = "\n".join(e.text for e in elements if e.text)

        words = text.split()
        if len(words) > 400:  # Limit to first 400 words
            text = " ".join(words[:400])
        
        document: Document = Document(page_content=text, metadata={'raw_heading': heading,
                                                                   'page_start': page_start,
                                                                   'page_end': page_end})
        
        return document

    def run(self) -> List[Document]:
        
        LOGGER.info(f"Starting Document Chunking for {len(self.elements)} elements")

        chunks: List[Document] = []
        buffer: List[Element] = []
        curr_heading = None
        page_start = None

        for element in self.elements:

            if isinstance(element, Title):

                if buffer:
                    chunks.append(
                        self.__build_chunk(
                            heading=curr_heading,
                            elements=buffer,
                            page_start=page_start,
                            page_end=buffer[-1].metadata.page_number
                        )
                    )
                    buffer = []
                curr_heading = element.text
                page_start = element.metadata.page_number

            else:
                if element.text and len(element.text.strip()) > 20:  # Ignore very short elements
                    buffer.append(element)
        
        if buffer:
            self.__build_chunk(
                heading=curr_heading,
                elements=buffer,
                page_start=page_start,
                page_end=buffer[-1].metadata.page_number
            )
        
        LOGGER.info(f"Completed Document Chunking with total chunks: {len(chunks)}")

        return chunks


class ChunkScoreAnnotator(Stage):

    """
    This stage scores each document chunk based on the presence of key proposal-related keywords
    and structural attributes. Each chunk is assigned a score that reflects its relevance to proposal content.
    """
    def __init__(self, chunks: List[Document]):
        super().__init__()
        self.chunks = chunks

    def __score_chunk(self, chunk: Document) -> tuple[int, Document]:
        text = chunk.page_content.lower()
        score = 0

        if chunk.metadata['raw_heading']:
            for keyword, weight in WEIGHTED_PROPOSAL_KEYWORDS.items():
                if keyword in chunk.metadata['raw_heading'].lower():
                    score += weight
                    chunk.metadata['section'] = keyword
                    break
        
        for keyword, weight in WEIGHTED_PROPOSAL_KEYWORDS.items():
            if keyword in text:
                score += 1  # Additive for body text presence
        
        words = text.split()

        if len(words) > 150:  # Length bonus
            score += 2
        
        if "table of contents" in text:  # Penalize if chunk is a table of contents
            score -= 5
        
        if "section" not in chunk.metadata:  # Penalize if no section identified
            score -= 100
        
        return score, chunk

    def run(self) -> List[Document]:
        LOGGER.info("Starting Chunk Scoring")

        for idx, chunk in enumerate(self.chunks):
            score, chunk = self.__score_chunk(chunk)
            chunk.metadata['chunk_score'] = score
            self.chunks[idx] = chunk
        
        LOGGER.info(f"Completed Chunk Scoring for {len(self.chunks)} chunks")

        return self.chunks



class FilterChunks(Stage):

    """
    This stage filters out document chunks that have a score below a certain threshold.
    Only chunks with a score of 4 or higher are retained for further processing.
    """

    def __init__(self, chunks: List[Document]):
        super().__init__()
        self.chunks = chunks
    
    def run(self) -> List[Document]:
        LOGGER.info("Starting Chunk Filtering")

        filtered_chunks: List[Document] = []

        for chunk in self.chunks:
            if chunk.metadata['chunk_score'] >= 4:  # Threshold for filtering
                filtered_chunks.append(chunk)
        
        LOGGER.info(f"Completed Chunk Filtering. Total chunks after filtering: {len(filtered_chunks)} out of {len(self.chunks)}")

        return filtered_chunks


if __name__ == '__main__':

    from proposal.core.logging_setup import setup_logging

    setup_logging()

    elements = partition_pdf(
        filename='data/raw/proposals/proposal-13.pdf',
        strategy="hi_res",
        infer_table_structure=True
    )

    elements = ProposalRelevanceCheck(
        elements=elements
    ).run()

    chunks = DocumentChunker(elements=elements).run()
    chunks = ChunkScoreAnnotator(chunks=chunks).run()
    chunks = FilterChunks(chunks=chunks).run()