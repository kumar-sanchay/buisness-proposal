import logging
from typing import Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel

from proposal.core.graph_state import GraphState
from proposal.chains import get_problem_statement_summary


LOGGER = logging.getLogger(__name__)


def get_summarize_problem_node(llm: BaseChatModel):
    def summarize_problem_statement_node(state: GraphState) -> Dict[str, Any]:

        LOGGER.info("Starting node: summarize_problem_statement_node")

        summarized_problem : str = state['summarized_problem_keys']

        if not summarized_problem:
            LOGGER.info("No summarized problem statement found in state; generating summary.")
            summarized_problem: str = get_problem_statement_summary(llm).invoke({
                'problem_statement': state['user_requirement']['problem_statement']
            })

        return {'summarized_problem_keys': summarized_problem}
    
    return summarize_problem_statement_node