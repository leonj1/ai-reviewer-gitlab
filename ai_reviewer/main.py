import os
import sys

from .llm_client import LLMClient
from .gitlab_reviewer import GitLabReviewer
from .review_strategies import StandardReviewStrategy, SecurityReviewStrategy


def main() -> None:
    """Main entry point for the GitLab AI reviewer."""
    # Check for required environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Error: OPENAI_API_KEY environment variable must be set")
        sys.exit(1)

    # Initialize components
    llm_client = LLMClient(api_key=openai_key)
    strategies = [StandardReviewStrategy(llm_client), SecurityReviewStrategy()]
    reviewer = GitLabReviewer(strategies)

    # Get GitLab CI/CD environment variables
    project_id = os.getenv("CI_PROJECT_ID")  # GitLab CI provides this
    mr_iid = os.getenv("CI_MERGE_REQUEST_IID")  # GitLab CI provides this

    # Fallback to manual environment variables if not in CI/CD
    if not project_id:
        project_id = os.getenv("GITLAB_PROJECT_ID")
    if not mr_iid:
        mr_iid = os.getenv("GITLAB_MR_IID")

    if not project_id or not mr_iid:
        print(
            "Error: Either CI_PROJECT_ID and CI_MERGE_REQUEST_IID must be set (in GitLab CI)"
        )
        print("or GITLAB_PROJECT_ID and GITLAB_MR_IID must be set (for local testing)")
        sys.exit(1)

    # Review the merge request
    reviewer.process_merge_request(int(project_id), int(mr_iid))


if __name__ == "__main__":
    main()
