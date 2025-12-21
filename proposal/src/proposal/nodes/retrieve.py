import logging
from typing import Dict, Any, List
from langchain_core.runnables import Runnable
from langchain_community.docstore.document import Document

from proposal.core.graph_state import GraphState

logger = logging.getLogger(__name__)


def get_retriever_node(retriever: Runnable):
    def retriever_node(state: GraphState) -> Dict[str, Any]:
        
        logger.info("Starting node: retriever_node")

        problem_statement: str = state['user_requirement']['problem_statement']
        documents: List[Document] = retriever.invoke(problem_statement)

        logger.info(f"Retrieved {len(documents)} documents.")
        return {'documents': documents}
    
    return retriever_node