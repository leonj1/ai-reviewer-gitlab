import pytest
from typing import Any, Dict
from ai_reviewer.gitlab_reviewer import GitLabReviewer
from ai_reviewer.review_strategies import ReviewComment


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


# Test cases for merge request processing
mr_process_test_cases = [
    pytest.param(
        # Test case 1: Single strategy, single comment
        {
            "project_id": 1,
            "mr_iid": 100,
            "changes": [
                {
                    "new_path": "test.py",
                    "diff": 'print("test")',
                    "line": 1,
                }
            ],
            "strategy_results": [
                [create_test_comment("test.py", 1, "Test comment")],
            ],
        },
        id="single_strategy_single_comment",
    ),
    pytest.param(
        # Test case 2: Multiple strategies, multiple comments
        {
            "project_id": 2,
            "mr_iid": 200,
            "changes": [
                {
                    "new_path": "multiple.py",
                    "diff": "def test():\n    pass",
                    "line": 1,
                }
            ],
            "strategy_results": [
                [create_test_comment("multiple.py", 1, "AI comment")],
                [create_test_comment("multiple.py", 1, "Security comment")],
            ],
        },
        id="multiple_strategies_multiple_comments",
    ),
]


@pytest.mark.parametrize("test_case", mr_process_test_cases)
def test_process_merge_request(mocker: Any, test_case: Dict[str, Any]) -> None:
    """Test merge request processing.

    Args:
        mocker: Pytest mocker fixture
        test_case: Test case data
    """
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "GITLAB_TOKEN": "test-token",
        },
    )

    # Mock GitLab client
    mock_gl = mocker.Mock()
    mock_project = mocker.Mock()
    mock_mr = mocker.Mock()

    # Setup mock returns
    mock_gl.projects.get.return_value = mock_project
    mock_project.mergerequests.get.return_value = mock_mr
    mock_mr.changes.return_value = {"changes": test_case["changes"]}

    # Mock strategies
    mock_strategies = []
    for result in test_case["strategy_results"]:
        strategy = mocker.Mock()
        strategy.review_changes.return_value = result
        mock_strategies.append(strategy)

    # Mock GitLab class
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance
    reviewer = GitLabReviewer(mock_strategies)

    # Execute
    reviewer.process_merge_request(test_case["project_id"], test_case["mr_iid"])

    # Verify
    mock_gl.projects.get.assert_called_once_with(test_case["project_id"])
    mock_project.mergerequests.get.assert_called_once_with(test_case["mr_iid"])
    mock_mr.changes.assert_called_once()

    # Verify each strategy was called
    for strategy in mock_strategies:
        strategy.review_changes.assert_called_once()

    # Verify comments were submitted
    expected_comment_count = sum(
        len(results) for results in test_case["strategy_results"]
    )
    assert mock_mr.discussions.create.call_count == expected_comment_count
