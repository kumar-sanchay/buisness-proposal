from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel


def get_problem_statement_summary(llm: BaseChatModel) -> str:

    system = "You are an information extraction assistant."
    human = """
        Extract the main searchable keywords and short noun phrases from the following
        problem statement.

        Rules:
        - Use only nouns or short noun phrases
        - Keep it concise (only 5 fix)
        - Separate items with commas
        - No sentences, no explanations
        - Return just final ouput no explainations.

        Problem statement:
        {problem_statement}
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', system),
            ('human', human)
        ]
    )
    return prompt | llm | StrOutputParser()