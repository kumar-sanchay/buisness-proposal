import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from proposal.core.schemas import DocumentSearchQuery
from proposal.chains import get_client_search_queries


class MockLLM(BaseChatModel):

    def _generate(self, messages, stop = None, run_manager = None, **kwargs):
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content="""
                        {
                            "search_queries": [
                                "Acme Corp company overview",
                                "Acme Corp industry analysis"
                            ]
                        }
                        """
                    ),
                    text=""  # REQUIRED
                )
            ]
        )

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"


def test_get_client_search_queries():
    result = get_client_search_queries(MockLLM()).invoke({
        'client_name': 'test',
        'industry': 'test'
    })

    assert result is not None
    assert isinstance(result, DocumentSearchQuery)
    assert len(result.search_queries) == 2
    assert result.search_queries[0] == "Acme Corp company overview"
    assert result.search_queries[1] == "Acme Corp industry analysis"

