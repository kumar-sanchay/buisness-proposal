from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

from proposal.core.schemas import GradeDocuments


def get_document_grading_chain(llm: BaseChatModel) -> RunnableSequence:

    structured_llm_grader = llm.with_structured_output(GradeDocuments)
    system_prompt = """
    You are a grader assessing relevance of a retrieved document to a user's requirement. \n 
    If the document contains keyword(s) or semantic meaning related to the requirement, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the requirement.
    """

    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Retrieved Documents: {document}\n\nUser's requirement: {requirement}")
        ]
    )

    return grade_prompt | structured_llm_grader