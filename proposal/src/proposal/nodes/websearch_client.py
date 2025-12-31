import logging
from typing import List, Dict, Any
from langchain_tavily import TavilySearch
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.docstore.document import Document

from proposal.core.graph_state import GraphState
from proposal.chains import get_client_search_queries
from proposal.core.schemas import DocumentSearchQuery

LOGGER = logging.getLogger(__name__)


def get_websearch_client_node(llm: BaseChatModel, tavily: TavilySearch):
    def websearch_client_node(state: GraphState) -> Dict[str, Any]:

        LOGGER.info("Starting node: websearch_client_node")

        if state['client_websearch']:
            LOGGER.info("Client websearch results already exist in state; skipping web search.")
            return {'client_websearch': state['client_websearch']}

        client_name: str = state['user_requirement']['client_info']['client_name']
        client_industry: str = state['user_requirement']['client_info']['industry']

        if client_name or client_industry:
            doc_search_queries: DocumentSearchQuery = get_client_search_queries(llm).invoke(
                {
                    'client_name': client_name,
                    'industry': client_industry
                }
            )

            LOGGER.info(f"Generated {len(doc_search_queries.search_queries)} search queries for client.")
            LOGGER.info(f"Search Queries: {doc_search_queries.search_queries}")
            LOGGER.info("Performing web search...")

            web_results: List[Any] = tavily.batch(
                [{"query": q} for q in doc_search_queries.search_queries]
            )
            doc_results: List[Document] = []

            for result in web_results:
                result = result['results']
                joined_results = '\n'.join(res['content'] for res in result)
                doc_results.append(Document(page_content=joined_results))
            LOGGER.info(f"Web searched and obtained {len(doc_results)} documents for client.")
        else:
            LOGGER.info("No client name or industry provided; skipping web search.")
            doc_results = []

        return {
            'client_websearch': doc_results
        }
    return websearch_client_node