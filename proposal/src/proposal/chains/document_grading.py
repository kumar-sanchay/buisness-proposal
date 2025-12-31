from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence

from proposal.core.schemas import GradeDocuments


def get_document_grading_chain(llm: BaseChatModel) -> str:

    system_prompt = """
        You are a relevance grader for retrieval-augmented generation.

        Your task is to decide whether a retrieved document is USEFUL
        for writing a specific consulting proposal section.

        A document DOES NOT need to be a perfect or complete example.
        Partial relevance is sufficient.
    """

    human_prompt = """
        Assess whether the following document is relevant for generating
        the specified consulting proposal section.

        Grading rules:
        - Return "yes" if the document is even partially useful (≈10% \or more)
        for understanding structure, content, or language of the section.
        - Return "yes" if the document contains similar sections, headings,
        or proposal-style content.
        - Return "yes" if the document is relevant to any domain seperated by commas below.
        - Return "no" only if the document is completely unrelated
        (e.g., definitions, blogs, news, marketing pages).

        Output rules:
        - Respond with ONLY one word: yes or no
        - No explanations

        Section to generate:
        {section}

        Document content:
        {document}

        Domain:
        {requirement}

    """

    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt)
        ]
    )

    return grade_prompt | llm | StrOutputParser()