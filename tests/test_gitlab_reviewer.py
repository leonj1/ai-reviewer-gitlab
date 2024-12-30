import pytest
from typing import Any, Dict
import gitlab
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
    mock_changes = {"changes": test_case["changes"]}

    # Setup mock returns
    mock_gl.projects.get.return_value = mock_project
    mock_project.mergerequests.get.return_value = mock_mr
    mock_mr.changes.return_value = mock_changes

    # Mock GitLab class
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance
    reviewer = GitLabReviewer([])

    # Execute
    reviewer.process_merge_request(test_case["project_id"], test_case["mr_iid"])

    # Verify
    mock_gl.projects.get.assert_called_once_with(test_case["project_id"])
    mock_project.mergerequests.get.assert_called_once_with(test_case["mr_iid"])
    mock_mr.changes.assert_called_once()


def test_ci_job_token_auth(mocker: Any) -> None:
    """Test GitLab authentication with CI job token."""
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "CI_JOB_TOKEN": "ci-token",
        },
    )

    # Mock GitLab client
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gl = mocker.Mock()
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance
    GitLabReviewer([])

    # Verify CI job token was used
    mock_gitlab.assert_called_once_with(
        url="https://gitlab.example.com", job_token="ci-token"
    )


def test_gitlab_error_with_response_details(mocker: Any) -> None:
    """Test GitLab error handling with response details."""
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "GITLAB_TOKEN": "test-token",
        },
    )

    # Mock GitLab client
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gl = mocker.Mock()
    mock_gitlab.return_value = mock_gl

    # Create error with response details
    error = mocker.Mock(spec=["response_code", "response_body"])
    error.response_code = 404
    error.response_body = "Project not found"
    mock_gl.projects.get.side_effect = error

    # Create reviewer instance
    reviewer = GitLabReviewer([])

    # Execute and verify error handling
    with pytest.raises(SystemExit) as exc_info:
        reviewer.process_merge_request(1, 100)
    assert exc_info.value.code == 1


def test_add_review_comments_error_handling(mocker: Any) -> None:
    """Test error handling in _add_review_comments."""
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "GITLAB_TOKEN": "test-token",
        },
    )

    # Mock GitLab client
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gl = mocker.Mock()
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance
    reviewer = GitLabReviewer([])

    # Create mock merge request that fails to create discussions
    mock_mr = mocker.Mock()
    mock_mr.discussions.create.side_effect = Exception("Failed to create discussion")

    # Create test comments
    comments = [
        create_test_comment("test1.py", 1, "Comment 1"),
        create_test_comment("test2.py", 2, "Comment 2"),
    ]

    # Execute
    reviewer._add_review_comments(mock_mr, comments)

    # Verify both comments were attempted despite errors
    assert mock_mr.discussions.create.call_count == 2


def test_merge_request_changes_without_diff(mocker: Any) -> None:
    """Test processing changes when some files have no diff."""
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "GITLAB_TOKEN": "test-token",
        },
    )

    # Mock GitLab client
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gl = mocker.Mock()
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance
    reviewer = GitLabReviewer([])

    # Create mock merge request with mixed changes
    mock_mr = mocker.Mock()
    mock_mr.changes.return_value = {
        "changes": [
            {"new_path": "test1.py", "diff": "print('test')"},  # Has diff
            {"new_path": "test2.py"},  # No diff
            {"new_path": "test3.py", "diff": ""},  # Empty diff
            {"new_path": "test4.py", "diff": "def test(): pass"},  # Has diff
        ]
    }

    # Get changes
    changes = reviewer._get_merge_request_changes(mock_mr)

    # Verify only changes with diffs were processed
    assert len(changes) == 2
    assert changes[0]["new_path"] == "test1.py"
    assert changes[1]["new_path"] == "test4.py"


def test_missing_gitlab_config(mocker: Any) -> None:
    """Test error when GitLab configuration is missing."""
    # Mock environment variables with missing URL
    mocker.patch.dict("os.environ", {}, clear=True)

    # Create reviewer instance and verify error
    with pytest.raises(SystemExit) as exc_info:
        GitLabReviewer([])
    assert exc_info.value.code == 1


def test_gitlab_connection_error(mocker: Any) -> None:
    """Test error when GitLab connection fails."""
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "GITLAB_TOKEN": "test-token",
        },
    )

    # Mock GitLab client that fails to connect
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gl = mocker.Mock()
    mock_gl.auth.side_effect = gitlab.exceptions.GitlabAuthenticationError(
        "Invalid token", response_code=401
    )
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance and verify error
    with pytest.raises(SystemExit) as exc_info:
        GitLabReviewer([])
    assert exc_info.value.code == 1


def test_process_merge_request_error(mocker: Any) -> None:
    """Test error handling in process_merge_request."""
    # Mock environment variables
    mocker.patch.dict(
        "os.environ",
        {
            "GITLAB_URL": "https://gitlab.example.com",
            "GITLAB_TOKEN": "test-token",
        },
    )

    # Mock GitLab client
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gl = mocker.Mock()
    mock_gitlab.return_value = mock_gl

    # Create reviewer instance
    reviewer = GitLabReviewer([])

    # Mock error in process_merge_request
    mock_gl.projects.get.side_effect = Exception("Unexpected error")

    # Execute and verify error handling
    with pytest.raises(SystemExit) as exc_info:
        reviewer.process_merge_request(1, 100)
    assert exc_info.value.code == 1
