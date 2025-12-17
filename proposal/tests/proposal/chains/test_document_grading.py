import pytest
from langchain_core.runnables import RunnableSequence

from proposal.chains.document_grading import get_document_grading_chain
from tests.proposal.helpers.fake_llm import FakeChatLLM
from proposal.core.schemas import GradeDocuments


@pytest.fixture
def llm():
    return FakeChatLLM(GradeDocuments(binary_score='yes'))


def test_get_document_grading_chain_returns_runnable(llm):
    chain = get_document_grading_chain(llm)
    assert isinstance(chain, RunnableSequence)


def test_grading_chain_with_structured_output(llm):
    chain = get_document_grading_chain(llm)
    assert llm.structured_schema is GradeDocuments