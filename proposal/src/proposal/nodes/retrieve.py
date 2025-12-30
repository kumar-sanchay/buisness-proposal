import logging
from typing import Dict, Any, List
from langchain_core.runnables import Runnable
from langchain_community.docstore.document import Document

from proposal.core.graph_state import GraphState
from proposal.chains import get_problem_statement_summary

LOGGER = logging.getLogger(__name__)


def normalize_chroma_filter(filters: dict | None) -> dict | None:
    if not filters:
        return None

    # Already has an operator like $and / $or
    if any(k.startswith("$") for k in filters):
        return filters

    # Single key is allowed
    if len(filters) == 1:
        return filters

    # Multiple keys → wrap in $and
    return {"$and": [{k: v} for k, v in filters.items()]}


def get_retriever_node(llm, retriever, section: str):
    def retriever_node(state: GraphState) -> Dict[str, Any]:
        
        LOGGER.info("Starting node: retriever_node")

        problem_statement: str = state['user_requirement']['problem_statement']
        # documents: List[Document] = retriever.invoke(problem_statement)

        normalized_filter = normalize_chroma_filter({
            'industry': state['user_requirement']['client_info']['industry'],
            'section': section.lower()
        })

        summaried_statement = get_problem_statement_summary(llm=llm).invoke({'problem_statement': problem_statement})
        LOGGER.info(f"Summarized problem statement for retrieval: {summaried_statement}")

        documents: List[Document] = retriever.similarity_search(
            summaried_statement,
            k=3,
            filter=normalized_filter
        )

        LOGGER.info(f"Retrieved {len(documents)} documents.")

        user_req = state['user_requirement']
        user_req['problem_statement'] = summaried_statement

        return {'section_documents': documents, 'user_requirement': user_req}
    
    return retriever_node