from typing import TypedDict, List
from langgraph.graph import MessagesState


class ClientInfo(TypedDict):
    """
    Represent ClientInfo

    Attributes:
        client_name: Client's company name which will be used for websearch
        industry: Client's industry
    """
    client_name: str
    industry: str


class UserRequirement(TypedDict):
    """
    Represent UserRequirement
    
    Attributes:
        problem_statement: Problem Statement for proposal
        client_info: Client's Info
        proposal_goal: Goal of the proposal
        approach: Approach to be taken
        timeline: Timeline for the project
        scope_exclusions: Scope and Exclusions
        budget_range: Budget Range
        technical_depth: Technical Depth required
    """
    problem_statement: str
    client_info: ClientInfo
    proposal_goal: str
    approach: str
    timeline: str
    scope_exclusions: str
    budget_range: str
    technical_depth: str


class GraphState(TypedDict):
    """
    Represent state of our graph.

    Attributes:
        user_requirement: UserRequirement provided by user
        documents: List of retrieved documents from vector DB
        client_websearch: List of websearch results for the client
        generated_section: Generated proposal section
    """
    user_requirement: UserRequirement
    documents: List[str]
    client_websearch: List[str]
    generated_section: str