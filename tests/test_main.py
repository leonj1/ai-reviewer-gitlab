import pytest
from unittest.mock import Mock
import os
import sys
from ai_reviewer.main import main


@pytest.fixture
def mock_environment(monkeypatch):
    """Set up a clean environment for each test."""
    # Clear relevant environment variables
    for var in [
        "OPENAI_API_KEY",
        "CI_PROJECT_ID",
        "CI_MERGE_REQUEST_IID",
        "GITLAB_PROJECT_ID",
        "GITLAB_MR_IID",
        "GITLAB_URL",
        "GITLAB_TOKEN",
        "CI_SERVER_URL",
        "CI_JOB_TOKEN",
    ]:
        monkeypatch.delenv(var, raising=False)


def test_missing_openai_key(mock_environment, capsys):
    """Test error when OPENAI_API_KEY is not set."""
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: OPENAI_API_KEY environment variable must be set" in captured.out


def test_missing_gitlab_variables(mock_environment, monkeypatch, capsys):
    """Test error when GitLab variables are not set."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "CI_PROJECT_ID or GITLAB_PROJECT_ID must be set" in captured.out


def test_gitlab_ci_variables(mock_environment, monkeypatch, mocker):
    """Test successful execution with GitLab CI variables."""
    # Mock environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("CI_PROJECT_ID", "123")
    monkeypatch.setenv("CI_MERGE_REQUEST_IID", "456")
    monkeypatch.setenv("GITLAB_URL", "https://gitlab.example.com")
    monkeypatch.setenv("GITLAB_TOKEN", "test-token")

    # Mock GitLab client
    mock_gl = Mock()
    mock_project = Mock()
    mock_mr = Mock()
    mock_changes = {"changes": [{"new_path": "test.py", "diff": "test"}]}

    # Setup mock returns
    mock_gl.projects.get.return_value = mock_project
    mock_project.mergerequests.get.return_value = mock_mr
    mock_mr.changes.return_value = mock_changes

    # Mock GitLab class
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gitlab.return_value = mock_gl

    # Mock strategies
    mock_strategy = Mock()
    mock_strategy.review_changes.return_value = []
    mocker.patch(
        "ai_reviewer.review_strategies.StandardReviewStrategy"
    ).return_value = mock_strategy
    mocker.patch(
        "ai_reviewer.review_strategies.SecurityReviewStrategy"
    ).return_value = mock_strategy

    # Run main
    main()

    # Verify GitLab interactions
    mock_gl.projects.get.assert_called_once_with(123)
    mock_project.mergerequests.get.assert_called_once_with(456)


def test_local_environment_variables(mock_environment, monkeypatch, mocker):
    """Test successful execution with local environment variables."""
    # Mock environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GITLAB_PROJECT_ID", "789")
    monkeypatch.setenv("GITLAB_MR_IID", "101")
    monkeypatch.setenv("GITLAB_URL", "https://gitlab.example.com")
    monkeypatch.setenv("GITLAB_TOKEN", "test-token")

    # Mock GitLab client
    mock_gl = Mock()
    mock_project = Mock()
    mock_mr = Mock()
    mock_changes = {"changes": [{"new_path": "test.py", "diff": "test"}]}

    # Setup mock returns
    mock_gl.projects.get.return_value = mock_project
    mock_project.mergerequests.get.return_value = mock_mr
    mock_mr.changes.return_value = mock_changes

    # Mock GitLab class
    mock_gitlab = mocker.patch("gitlab.Gitlab")
    mock_gitlab.return_value = mock_gl

    # Mock strategies
    mock_strategy = Mock()
    mock_strategy.review_changes.return_value = []
    mocker.patch(
        "ai_reviewer.review_strategies.StandardReviewStrategy"
    ).return_value = mock_strategy
    mocker.patch(
        "ai_reviewer.review_strategies.SecurityReviewStrategy"
    ).return_value = mock_strategy

    # Run main
    main()

    # Verify GitLab interactions
    mock_gl.projects.get.assert_called_once_with(789)
    mock_project.mergerequests.get.assert_called_once_with(101)
