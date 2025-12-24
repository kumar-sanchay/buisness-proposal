import pytest
from unittest.mock import Mock
from langchain_core.runnables import Runnable
from langchain_community.docstore.document import Document

from proposal.nodes import get_retriever_node
from proposal.core.graph_state import GraphState, UserRequirement


def test_retriever_node():
    retriever = Mock(Runnable)
    return_val = [Document(page_content='test')] * 3
    retriever.invoke.return_value = return_val
    user_requirement = UserRequirement(problem_statement='Test Problem')
    state = GraphState(user_requirement=user_requirement)

    updated_state = get_retriever_node(retriever)(state)

    assert 'documents' in updated_state
    assert len(updated_state['documents']) == 3
    assert updated_state['documents'] == return_val


def test_retriever_node_with_empty_state():
    retriever = Mock(Runnable)
    return_val = [Document(page_content='test')]
    retriever.invoke.return_value = return_val
    state = GraphState()

    with pytest.raises(KeyError):
        updated_state = get_retriever_node(retriever)(state)


def test_retriever_node_with_retriever_output():
    retriever = Mock(Runnable)
    retriever.invoke.return_value = []
    user_requirement = UserRequirement(problem_statement='Test Problem')
    state = GraphState(user_requirement=user_requirement)

    updated_state = get_retriever_node(retriever)(state)
    assert 'documents' in updated_state
    assert len(updated_state['documents']) == 0
    assert updated_state['documents'] == []