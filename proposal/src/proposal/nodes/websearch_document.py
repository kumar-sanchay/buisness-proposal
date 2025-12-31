import logging
from typing import List, Dict, Any
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.docstore.document import Document
from langchain_core.messages import AIMessage

from proposal.core.graph_state import GraphState
from proposal.chains import get_section_search_queries
from proposal.core.schemas import DocumentSearchQuery
from proposal.indexing.document_pipeline import run_pipeline


LOGGER = logging.getLogger(__name__)


def get_websearch_document_node(llm: BaseChatModel, tavily: TavilySearchResults):
    def websearch_document_node(state: GraphState) -> Dict[str, Any]:
        
        LOGGER.info(f"Starting node: websearch_document_node")

        client_industry: str = state['user_requirement']['client_info']['industry']

        doc_search_queries: DocumentSearchQuery = get_section_search_queries(llm).invoke({
            'proposal_section': state['curr_section_heading'],
            'industry': client_industry,
            'generated_queries': "\n".join(state['generated_section_queries']),
            "problem_statement": state['user_requirement']['problem_statement']     
        })

        LOGGER.info(f"Generated {len(doc_search_queries.search_queries)} search queries for section {state['curr_section_heading']}.")
        LOGGER.info(f"Search Queries: {doc_search_queries.search_queries}")

        LOGGER.info("Performing web search...")
        web_results: List[Any] = tavily.batch(
                [{"query": q} for q in doc_search_queries.search_queries]
        )

        for results in web_results:
            for result in results:
                url: str = result.get('url')
                is_passed: bool = run_pipeline(url, industry=client_industry)
                LOGGER.info(f"Document at URL {url} passed the pipeline: {is_passed}")
        
        return {'generated_section_queries': state['generated_section_queries'] + doc_search_queries.search_queries,
                'doc_search_iter_count': state['doc_search_iter_count'] + 1
                }
    
    return websearch_document_node