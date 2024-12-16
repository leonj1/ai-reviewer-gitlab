import os
from .llm_client import LLMClient
from .gitlab_reviewer import GitLabReviewer
from .review_strategies import StandardReviewStrategy, SecurityReviewStrategy


def main() -> None:
    """Main entry point for the GitLab AI reviewer."""
    llm_client = LLMClient(api_key=os.getenv("OPENAI_API_KEY", ""))
    strategies = [StandardReviewStrategy(llm_client), SecurityReviewStrategy()]
    reviewer = GitLabReviewer(strategies)

    project_id = os.getenv("GITLAB_PROJECT_ID")
    mr_iid = os.getenv("GITLAB_MR_IID")

    if not project_id or not mr_iid:
        print("Error: GITLAB_PROJECT_ID and GITLAB_MR_IID must be set")
        return

    reviewer.process_merge_request(int(project_id), int(mr_iid))


if __name__ == "__main__":
    main()
