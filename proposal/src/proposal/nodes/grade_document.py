import logging
from typing import Dict, Any, List
from langchain_core.runnables import Runnable
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.docstore.document import Document

from proposal.core.graph_state import GraphState
from proposal.core.schemas import GradeDocuments
from proposal.chains import get_document_grading_chain

LOGGER = logging.getLogger(__name__)


def get_grade_document_node(llm: BaseChatModel, proposal_section: str):
    def grade_document(state: GraphState) -> Dict[str, Any]:

        LOGGER.info(f"Starting node: grade_document for section")

        documents: List[Document] = state['section_documents']
        relevant_docs: List[Document] = []

        for doc in documents:
            score: str = get_document_grading_chain(llm).invoke({
                'document': doc,
                'requirement': state['user_requirement']['problem_statement'],
                'section': proposal_section,
            })

            if score == 'yes':
                relevant_docs.append(doc)
        
        LOGGER.info(f"Graded documents, {len(relevant_docs)} relevant for section {proposal_section}.")

        return {'section_documents': relevant_docs}

    return grade_document