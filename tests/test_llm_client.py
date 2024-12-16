import pytest
from typing import Any, Dict, List
from llm_client import LLMClient
from review_strategies import ReviewComment


@pytest.fixture
def mock_openai(mocker: Any) -> Any:
    """Mock OpenAI API responses.

    Args:
        mocker: Pytest mocker fixture
    Returns:
        Mock object for OpenAI API
    """
    mock = mocker.patch("openai.chat.completions.create")
    mock.return_value.choices = [
        type("Choice", (), {"message": {"content": "Test feedback"}})()
    ]
    return mock


def test_analyze_code(mock_openai: Any) -> None:
    """Test code analysis with mock OpenAI response.

    Args:
        mock_openai: Mock OpenAI API fixture
    """
    client = LLMClient("test-key")
    changes: List[Dict[str, Any]] = [
        {
            "new_path": "test.py",
            "diff": "print('hello')",
            "line": 1,
        }
    ]

    comments: List[ReviewComment] = client.analyze_code(changes)

    assert len(comments) == 1
    assert isinstance(comments[0], ReviewComment)
    assert comments[0].path == "test.py"
    assert comments[0].line == 1
    assert comments[0].content == "Test feedback"


def test_analyze_code_error_handling(mocker: Any) -> None:
    """Test error handling during code analysis.

    Args:
        mocker: Pytest mocker fixture
    """
    mocker.patch(
        "openai.ChatCompletion.create",
        side_effect=Exception("API Error"),
    )
    client = LLMClient("test-key")
    changes: List[Dict[str, Any]] = [{"new_path": "test.py", "diff": "code", "line": 1}]

    comments: List[ReviewComment] = client.analyze_code(changes)
    assert len(comments) == 0
