import pytest
from typing import Any, Dict, List

from ai_reviewer.review_strategies import (
    ReviewComment,
    SecurityReviewStrategy,
    StandardReviewStrategy,
)


def create_test_comment(path: str, line: int, content: str) -> ReviewComment:
    """Create a test review comment.

    Args:
        path: File path
        line: Line number
        content: Comment content
    Returns:
        ReviewComment instance
    """
    return ReviewComment(path=path, line=line, content=content)


# Test cases for AI review strategy
ai_review_test_cases = [
    pytest.param(
        # Test case 1: Simple Python code
        {
            "changes": [
                {
                    "new_path": "test.py",
                    "diff": 'print("test")',
                    "line": 1,
                }
            ]
        },
        [create_test_comment("test.py", 1, "Test comment")],
        id="simple_python_code",
    ),
    pytest.param(
        # Test case 2: Multiple files
        {
            "changes": [
                {
                    "new_path": "file1.py",
                    "diff": "def test():\n    pass",
                    "line": 1,
                },
                {
                    "new_path": "file2.py",
                    "diff": "class Test:\n    pass",
                    "line": 1,
                },
            ]
        },
        [
            create_test_comment("file1.py", 1, "Comment 1"),
            create_test_comment("file2.py", 1, "Comment 2"),
        ],
        id="multiple_files",
    ),
]


@pytest.mark.parametrize("changes,expected_comments", ai_review_test_cases)
def test_ai_review_strategy(
    mocker: Any,
    changes: Dict[str, List[Dict[str, Any]]],
    expected_comments: List[ReviewComment],
) -> None:
    """Test AI review strategy.

    Args:
        mocker: Pytest mocker fixture
        changes: Test changes data
        expected_comments: Expected review comments
    """
    # Mock LLM client
    mock_llm = mocker.Mock()
    mock_llm.analyze_code.return_value = expected_comments

    # Create strategy and run review
    strategy = StandardReviewStrategy(mock_llm)
    result = strategy.review_changes(changes["changes"])

    # Verify results
    assert result == expected_comments
    mock_llm.analyze_code.assert_called_once_with(changes["changes"])


# Test cases for security review strategy
security_review_test_cases = [
    pytest.param(
        # Test case 1: Code with security issues
        {
            "changes": [
                {
                    "new_path": "secure.py",
                    "diff": 'password = "secret123"',
                    "new_line": 5,
                }
            ]
        },
        [
            create_test_comment(
                "secure.py", 5, "Security Issue: Avoid hardcoding passwords"
            )
        ],
        id="security_issue_found",
    ),
    pytest.param(
        # Test case 2: Code without security issues
        {
            "changes": [
                {
                    "new_path": "safe.py",
                    "diff": "print('Hello, World!')",
                    "new_line": 1,
                }
            ]
        },
        [],
        id="no_security_issues",
    ),
]


@pytest.mark.parametrize("changes,expected_comments", security_review_test_cases)
def test_security_review_strategy(
    changes: Dict[str, List[Dict[str, Any]]],
    expected_comments: List[ReviewComment],
) -> None:
    """Test security review strategy.

    Args:
        changes: Test changes data
        expected_comments: Expected review comments
    """
    strategy = SecurityReviewStrategy()
    result = strategy.review_changes(changes["changes"])
    assert result == expected_comments
