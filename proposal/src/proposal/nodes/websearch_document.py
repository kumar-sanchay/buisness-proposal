from typing import List, Dict, Any
from langchain_tavily import TavilySearch
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.docstore.document import Document

from proposal.core.graph_state import GraphState
from proposal.chains import get_section_search_queries
from proposal.core.schemas import DocumentSearchQuery


def get_websearch_document_node(llm: BaseChatModel, proposal_section: str, tavily: TavilySearch):
    def websearch_document_node(state: GraphState) -> Dict[str, Any]:

        client_industry: str = state['user_requirement']['client_info']['industry']

        search_queries: DocumentSearchQuery = get_section_search_queries(llm).invoke({
            'proposal_section': proposal_section,
            'industry': client_industry
        })


        web_results: List[Any] = tavily.batch({{"query": query} for query in search_queries})
        doc_results: List[Document] = []

        for result in web_results:
            result = result['results']
            joined_result = "\n".join([res["content"] for res in result])
            doc_results.append(Document(page_content=joined_result))
        
        return {'documents': state['documents'] + doc_results}
    
    return websearch_document_node