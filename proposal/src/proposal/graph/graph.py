from dotenv import load_dotenv
from proposal.core.logging_setup import setup_logging
load_dotenv()
setup_logging()

from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearch
from langchain_community.tools.tavily_search import TavilySearchResults

from proposal.core.graph_state import GraphState, UserRequirement, ClientInfo
from proposal.graph import constants
from proposal.nodes import (get_generate_proposal_section_node, get_retriever_node, get_grade_document_node,
                            get_websearch_client_node, get_websearch_document_node)

from proposal.core.llm import get_llm
from proposal.indexing.vectorstore import get_retriever



def build_graph(user_requirement: UserRequirement, proposal_section: str = "Executive Summary"):
    llm = get_llm()
    tavily_search = TavilySearch(max_results=2)

    tavily_search_results = TavilySearchResults(
        max_results=3,
        search_depth="advanced",
        include_raw_content=True,
    )
    retriever = get_retriever()

    graph = StateGraph(GraphState)
    graph.add_node(constants.RETRIEVE, get_retriever_node(llm= llm, retriever=retriever, section=proposal_section))
    graph.add_node(constants.GRADE_DOCUMENTS, get_grade_document_node(llm=llm, proposal_section=proposal_section))
    graph.add_node(constants.WEBSEARCH_DOCUMENT, get_websearch_document_node(llm=llm, proposal_section=proposal_section,
                                                                              tavily=tavily_search_results))
    graph.add_node(constants.WEBSEARCH_CLIENT, get_websearch_client_node(llm=llm, tavily=tavily_search))
    graph.add_node(constants.GENERATE, get_generate_proposal_section_node(llm=llm, proposal_section=proposal_section))

    graph.set_entry_point(constants.RETRIEVE)
    graph.add_edge(constants.RETRIEVE, constants.GRADE_DOCUMENTS)

    def web_search_document_condition(state: GraphState):

        if len(state["section_documents"]) >= 1:
            return constants.WEBSEARCH_CLIENT
        return constants.WEBSEARCH_DOCUMENT
    
    graph.add_conditional_edges(constants.GRADE_DOCUMENTS,
                                web_search_document_condition,
                                {
                                    constants.WEBSEARCH_CLIENT: constants.WEBSEARCH_CLIENT,
                                    constants.WEBSEARCH_DOCUMENT: constants.WEBSEARCH_DOCUMENT
                                }
        )
    
    graph.add_edge(constants.WEBSEARCH_DOCUMENT, constants.RETRIEVE)
    graph.add_edge(constants.WEBSEARCH_CLIENT, constants.GENERATE)
    graph.add_edge(constants.GENERATE, END)

    app = graph.compile()
    # app.get_graph().draw_mermaid_png(output_file_path="test_graph.png")
    
    # test_user_requirement: UserRequirement = {
    #     "problem_statement": (
    #         "The client is struggling with slow and inconsistent creation of "
    #         "custom consulting proposals, leading to longer sales cycles and "
    #         "reduced win rates."
    #     ),
    #     "client_info": {
    #         "client_name": "Acme Financial Services",
    #         "industry": "Banking and Financial Services"
    #     },
    #     "proposal_goal": (
    #         "Design and implement an AI-powered consulting proposal generator "
    #         "that can create high-quality, client-specific proposal sections "
    #         "using internal knowledge and external research."
    #     ),
    #     "approach": (
    #         "Leverage Retrieval-Augmented Generation (RAG) with a modular "
    #         "LangGraph-based workflow. Use vector databases for internal content, "
    #         "web search for external insights, and LLM-based scoring and refinement "
    #         "for proposal sections."
    #     ),
    #     "timeline": "8–10 weeks including discovery, implementation, testing, and rollout",
    #     "scope_exclusions": (
    #         "Does not include CRM integration, UI/UX design for a sales portal, "
    #         "or long-term model fine-tuning beyond initial deployment."
    #     ),
    #     "budget_range": "USD 50,000 – 75,000",
    #     "technical_depth": "Medium to High (target audience includes technical decision-makers)"
    # }
    initial_state = GraphState(
        user_requirement=user_requirement,
        documents=[],
        client_websearch=[],
        generated_section="",
        generated_section_queries=[]
    )

    result: GraphState = app.invoke(initial_state)
    return result["generated_section"]


if __name__ == '__main__':
    user_requirement: UserRequirement = {
        "problem_statement": '',
        "client_info": {
            "client_name": '',
            "industry": '',
        },
        "proposal_goal": '',
        "approach": '',
        "timeline": '',
        "scope_exclusions": '',
        "budget_range": '',
        "technical_depth": '',
    }
    build_graph(user_requirement=user_requirement)