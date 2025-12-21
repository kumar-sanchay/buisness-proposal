import logging
from typing import List, Dict, Any
from langchain_community.docstore.document import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage

from proposal.core.graph_state import GraphState
from proposal.chains import generate_proposal_section

logger = logging.getLogger(__name__)

def format_docs(docs: List[Document]):
    return "\n".join([doc.page_content for doc in docs])


def get_generate_proposal_section_node(llm: BaseChatModel, proposal_section: str):
    def generate_proposal_section_node(state: GraphState) -> Dict[str, Any]:

        logger.info(f"Starting node: generate_proposal_section_node")

        generate_section: AIMessage = generate_proposal_section(llm).invoke(
            {
                'section_name': proposal_section,
                'problem_statement': state['user_requirement']['problem_statement'],
                'proposal_goal': state['user_requirement']['proposal_goal'],
                'approach': state['user_requirement']['approach'],
                'timeline': state['user_requirement']['timeline'],
                'scope_exclusions': state['user_requirement']['scope_exclusions'],
                'budget_range': state['user_requirement']['budget_range'],
                'technical_depth': state['user_requirement']['technical_depth'],
                'client_name': state['user_requirement']['client_info']['client_name'],
                'industry': state['user_requirement']['client_info']['industry'],
                'documents': format_docs(state['documents']),
                'client_websearch': format_docs(state['client_websearch'])
            }
        )

        logger.info(f"Generated proposal section: {proposal_section}")
        logger.info(f"Section Content: {generate_section.content}")

        return {
            'generated_section': generate_section.content
        }
    return generate_proposal_section_node