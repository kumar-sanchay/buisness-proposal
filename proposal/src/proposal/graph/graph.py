import logging
from typing import List, Dict, Generator, Tuple
from langgraph.graph import StateGraph, END
from langchain_tavily import TavilySearch
from langchain_community.tools.tavily_search import TavilySearchResults

from proposal.core.graph_state import GraphState, UserRequirement, ClientInfo
from proposal.graph import constants
from proposal.nodes import (get_generate_proposal_section_node, get_retriever_node, get_grade_document_node,
                            get_websearch_client_node, get_websearch_document_node, get_summarize_problem_node)

from proposal.core.llm import get_llm
from proposal.indexing.vectorstore import get_retriever


LOGGER = logging.getLogger(__name__)
MAX_DOC_SEARCH_ITERATION = 2


def build_graph():

    llm = get_llm()
    tavily_search = TavilySearch(max_results=2)

    tavily_search_results = TavilySearchResults(
        max_results=3,
        search_depth="advanced",
        include_raw_content=True,
    )
    retriever = get_retriever()

    graph = StateGraph(GraphState)
    graph.add_node(constants.SUMMARIZE_PROBLEM, get_summarize_problem_node(llm=llm))
    graph.add_node(constants.RETRIEVE, get_retriever_node(llm=llm, retriever=retriever))
    graph.add_node(constants.GRADE_DOCUMENTS, get_grade_document_node(llm=llm))
    graph.add_node(constants.WEBSEARCH_DOCUMENT, get_websearch_document_node(llm=llm, tavily=tavily_search_results))
    graph.add_node(constants.WEBSEARCH_CLIENT, get_websearch_client_node(llm=llm, tavily=tavily_search))
    graph.add_node(constants.GENERATE, get_generate_proposal_section_node(llm=llm))

    graph.set_entry_point(constants.SUMMARIZE_PROBLEM)
    graph.add_edge(constants.SUMMARIZE_PROBLEM, constants.RETRIEVE)
    graph.add_edge(constants.RETRIEVE, constants.GRADE_DOCUMENTS)

    def web_search_document_condition(state: GraphState):

        if len(state["section_documents"]) >= 1 or state["doc_search_iter_count"] >= MAX_DOC_SEARCH_ITERATION:
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

    compiled_graph = graph.compile()
    # app.get_graph().draw_mermaid_png(output_file_path="test_graph.png")

    return compiled_graph


def run_graph(
    user_requirement: UserRequirement,
    proposal_sections: List[str],
) -> Generator[Tuple[str, str, str], None, Dict[str, str]]:

    graph = build_graph()
    section_output_map: Dict[str, str] = {}

    initial_state = GraphState(
        user_requirement=user_requirement,
        client_websearch=[],
        summarized_problem_keys=""
    )

    for section in proposal_sections:
        LOGGER.info(f"Generating proposal section: {section}")


        initial_state.update({
            "curr_section_heading": section,
            "doc_search_iter_count": 0,
            "generated_section": "",
            "generated_section_queries": [],
            "section_documents": []
        })

        final_state = None

        for event in graph.stream(initial_state):

            if isinstance(event, dict) and "event" in event:
                node_name = event.get("name", "Unknown Node")
                event_type = event["event"]

                yield section, node_name, event_type

                if event_type == "on_chain_end" and event.get("state"):
                    final_state = event["state"]

            elif isinstance(event, dict) and len(event) == 1:
                node_name = list(event.keys())[0]

                yield section, node_name, "node_output"

            elif isinstance(event, dict) and "state" in event:
                yield section, "Graph State", "state_update"
                final_state = event["state"]

            else:
                yield section, "Graph", "unknown_event"
        
        if event and event.get("generate"):
            section_output_map[section] = event['generate']['generated_section']
        else:
            section_output_map[section] = ""

        LOGGER.info(f"Completed proposal section: {section}")

    return section_output_map



if __name__ == '__main__':

    from dotenv import load_dotenv
    from proposal.core.logging_setup import setup_logging
    load_dotenv()
    setup_logging()

    sections = [
        "Executive Summary",
        "Approach",
        "Timeline"
    ]
    
    user_requirement: UserRequirement = {
        "problem_statement": 'The firm relies on fragmented data sources and manual research processes for investment analysis,'
        ' risk assessment, and regulatory review. This results in slower decision-making, inconsistent insights across teams, '
        'higher operational costs, and increased compliance risk in a fast-moving market environment.',
        "client_info": {
            "client_name": 'Acme Financial Services',
            "industry": 'Banking and Financial Services',
        },
        "proposal_goal": 'To implement an AI-enabled solution that automates financial document analysis and research workflows,'
        ' improves decision accuracy and speed, reduces operational effort, and strengthens compliance across investment and banking operations.',
        "approach": '',
        "timeline": '',
        "scope_exclusions": '',
        "budget_range": '',
        "technical_depth": '',
    }
    print(run_graph(user_requirement=user_requirement, proposal_sections=sections))