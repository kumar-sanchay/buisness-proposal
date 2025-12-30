import os
from typing import List
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.docstore.document import Document

from proposal.core.embeddings import get_bge_embeddings


def get_retriever():
    vectorstore = Chroma(
        collection_name=os.getenv("CHROMA_DB_COLLECTION_NAME"),
        persist_directory=os.getenv("CHROMADB_DIRECTORY"),
        embedding_function=get_bge_embeddings(),
    )

    return vectorstore


def save_documents(documents: List[Document]):
    if documents:
        Chroma.from_documents(
            documents=documents,
            embedding=get_bge_embeddings(),
            collection_name=os.getenv('CHROMA_DB_COLLECTION_NAME'),
            persist_directory=os.getenv('CHROMADB_DIRECTORY')
        )