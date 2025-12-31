from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from proposal.core.schemas import DocumentSearchQuery


def get_client_search_queries(llm: BaseChatModel):

    system_prompt = """
        You are an expert consulting researcher.
        Your task is to generate a list of 2 web search queries list that will be used to find about the client and
        client's industry as given below.
    """

    human_prompt = """
        Client name: {client_name}
        Client's Industry: {industry}

        RULES:
        1) Output should be strictly just json like given format below

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

    output_parser = PydanticOutputParser(pydantic_object=DocumentSearchQuery)

    return query_prompt | llm | output_parser
    