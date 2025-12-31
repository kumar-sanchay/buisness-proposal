from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser

from proposal.core.schemas import DocumentSearchQuery



def get_section_search_queries(llm: BaseChatModel):


    system_prompt = """
        You are an expert research assistant helping to retrieve real-world consulting proposal PDFs from the web.
    """

    human_prompt = """
        You are given a problem statement describing a real-world consulting need.

        Generate strictly 3 short web search queries to find real consulting documents
        (strictly only PDFs), not blogs or definitions.

        Do not include full sentences.
        Structly No Queries should be repeated from "Generated Queries" from below.

        Generated Queries:
        {generated_queries}

        Inputs:
        - Section: {proposal_section}
        - Industry: {industry}
        - Problem Statement Keywords: {problem_statement}

        Rules:
        1) Output should be strictly in json like below.
        2) pdf should be added in query search query.
        3) Include exact section name in every query.
        4) Every search query should have "Consulting Service" or "Consulting Proposal" or "Service Proposal"

        Output format:
        {{
            "search_queries": ["query1", "query2", ..]
        }}
    """

    query_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt)
        ]
    )

    parser = PydanticOutputParser(pydantic_object=DocumentSearchQuery)
    return query_prompt | llm | parser
    