from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from proposal.core.schemas import DocumentSearchQuery


def get_client_search_queries(llm: BaseChatModel):

    structured_output = llm.with_structured_output(DocumentSearchQuery)

    system_prompt = """
        You are an expert consulting researcher.
        Your task is to generate a list of 1 to 3 web search queries list that will be used to find about the client and
        client's industry as given below.
        Don't generate search queries which are already generated. You can check that in messages.
    """

    query_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Client name: {client_name}\n\nClient's Industry: {industry}")
        ]
    )

    return query_prompt | structured_output
    