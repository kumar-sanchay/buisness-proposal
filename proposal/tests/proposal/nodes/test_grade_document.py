import pytest
from unittest.mock import patch, MagicMock
from proposal.nodes.grade_document import get_grade_document_node
from proposal.core.graph_state import GraphState


@patch('proposal.nodes.grade_document.get_document_grading_chain')
def test_grading_chain_mock(mock_grading_chain):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = MagicMock(binary_score='yes')
    mock_grading_chain.return_value = mock_chain

    llm = MagicMock()
    proposal_section = "Test Section"
    state = {
        'documents': [MagicMock(), MagicMock()],
        'user_requirement': "Test Requirement"
    }

    grade_document = get_grade_document_node(llm, proposal_section)
    result = grade_document(state)
    assert len(result['documents']) == 2


@patch('proposal.nodes.grade_document.get_document_grading_chain')
def test_grading_chain_mock_return_only_relevant_doc(mock_grading_chain):
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = [MagicMock(binary_score='yes'),
                                     MagicMock(binary_score='no')]
    mock_grading_chain.return_value = mock_chain

    llm = MagicMock()
    proposal_section = "Test Section"
    state = {
        'documents': [MagicMock(), MagicMock()],
        'user_requirement': "Test Requirement"
    }

    grade_document = get_grade_document_node(llm, proposal_section)
    result = grade_document(state)
    assert len(result['documents']) == 1  # only 1 document is relevant


def test_with_empty_document_state():
    llm = MagicMock()
    proposal_section = "Test Section"
    state = GraphState()

    grade_document = get_grade_document_node(llm, proposal_section)

    with pytest.raises(KeyError):
        result = grade_document(state)
