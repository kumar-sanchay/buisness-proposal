import os
from langchain_community.vectorstores.chroma import Chroma

from proposal.core.embeddings import get_bge_embeddings


def get_retriever():
    vectorstore = Chroma(
        collection_name=os.getenv('CHROMA_DB_COLLECTION_NAME'),
        persist_directory=os.getenv('CHROMADB_DIRECTORY'),
        embedding_function=get_bge_embeddings()
    )

    return vectorstore.as_retriever()