import tempfile
import requests
import logging
from typing import List
from pathlib import Path
from PyPDF2 import PdfReader
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Element
from langchain_community.docstore.document import Document

from proposal.indexing.stages import (
    ProposalRelevanceCheck,
    DocumentChunker,
    ChunkScoreAnnotator,
    FilterChunks
)
from proposal.indexing.vectorstore import save_documents

LOGGER = logging.getLogger(__name__)


def download_pdf_into_temp(url: str):

    try:
        LOGGER.info(f"Downloading PDF from URL: {url}")
        response = requests.get(url=url, stream=True, timeout=10)
        response.raise_for_status()

        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_file.write(response.content)
        pdf_file.close()

        return Path(pdf_file.name)
    except requests.RequestException as e:
        LOGGER.error("Error while downloading pdf: ", url)
        return None


def is_pdf_file(url: str) -> bool:
    
    try:
        resp = requests.head(url=url, allow_redirects=True, timeout=10)
        content_type = resp.headers.get("Content-Type", "").lower()
        return "application/pdf" in content_type
    except requests.RequestException as e:
        LOGGER.error("Error while downloading headers of url: ", url)
        return False



def is_pdf_pages_under_limit(path: str) -> bool:
    reader = PdfReader(path)
    LOGGER.info(f"PDF has {len(reader.pages)} pages.")
    return len(reader.pages) <= 50


def run_pipeline(url: str, industry: str) -> bool:
    
    LOGGER.info(f"Running document pipeline for URL: {url}")

    if not is_pdf_file(url=url):
        return False
        
    pdf_path = None

    try:
        pdf_path: Path = download_pdf_into_temp(url)

        if not (pdf_path and is_pdf_pages_under_limit(pdf_path)):
            return False

        elements: List[Element] = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            infer_table_structure=True
        )
        elements = ProposalRelevanceCheck(
        elements=elements).run()
        chunks: List[Document] = DocumentChunker(elements=elements).run()
        chunks = ChunkScoreAnnotator(chunks=chunks).run()
        chunks = FilterChunks(chunks=chunks).run()
        
        for chunk in chunks:
            chunk.metadata['industry'] = industry
            chunk.metadata['source_url'] = url

        save_documents(documents=chunks)

    except Exception as e:
        LOGGER.exception("Exception on parser pipeline: ", e)
        return False
    finally:
        if pdf_path:
            pdf_path.unlink()
    
    LOGGER.info(f"Completed document pipeline for URL: {url}")

    return True

