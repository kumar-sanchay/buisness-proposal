from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from proposal.core.schemas import DocumentSearchQuery


def get_section_search_queries(llm: BaseChatModel):

    structured_output = llm.with_structured_output(DocumentSearchQuery)

    system_prompt = """
        You are an expert consulting researcher.
        Your task is to generate a list of 1 to 3 web search queries list that will be used to find real consulting proposal section examples for a given proposal section.
        The queries should:
        1) Help find examples of the same proposal section from the web
        2) Prefer content from consulting firms, proposal templates, case studies, or whitepapers
        3) Be specific and actionable, not generic theory
        4) Focus on section-level examples, not full proposals or general concepts
    """

    query_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Section name: {proposal_section}\n\nClient's Industry: {industry}")
        ]
    )

    return query_prompt | structured_output
    