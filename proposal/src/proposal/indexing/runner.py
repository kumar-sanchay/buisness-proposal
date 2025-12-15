import os
import logging
from typing import List
from dotenv import load_dotenv
from langchain_community.docstore.document import Document
from langchain_community.vectorstores.chroma import Chroma

from proposal.indexing.parser import ProposalParser
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from proposal.core.logging_setup import setup_logging

load_dotenv()
setup_logging()


logger = logging.getLogger(__name__)


def main():

    logger.info("Starting indexing of raw proposal pdfs")

    pdf_data_dir: str = "data/raw/proposals"
    pdf_files_path: List[str] = [os.path.join(pdf_data_dir, pdf_file_name) for pdf_file_name in os.listdir(pdf_data_dir)]

    logger.info(f"Total pdf files which will be processed: {len(pdf_files_path)}")

    documents: List[Document] = [
        doc
        for pdf_path in pdf_files_path
        for doc in ProposalParser.parse(pdf_path)
    ]

    logger.info(f"Total documents fetched from raw proposal pdfs: {len(documents)}")
    logger.debug(f"Document Data: {documents[:2]}")


    bge_embedding = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=bge_embedding,
        collection_name=os.getenv('CHROMA_DB_COLLECTION_NAME'),
        persist_directory=os.getenv('CHROMADB_DIRECTORY')
    )

    logger.info("Documents stored in vectorstore.")


if __name__ == '__main__':
    main()