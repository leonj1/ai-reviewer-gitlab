import os
from typing import List, Dict, Any
import gitlab

from .review_strategies import ReviewStrategy, ReviewComment
from dotenv import load_dotenv


class GitLabReviewer:
    """Main class for handling GitLab merge request reviews."""

    def __init__(self, review_strategies: List[ReviewStrategy]) -> None:
        """Initialize GitLab reviewer with review strategies.

        Args:
            review_strategies: List of review strategies to apply
        """
        load_dotenv()
        self.strategies = review_strategies
        self.gl = gitlab.Gitlab(
            url=os.getenv("GITLAB_URL", ""),
            private_token=os.getenv("GITLAB_TOKEN", ""),
        )

    def process_merge_request(self, project_id: int, mr_iid: int) -> None:
        """Process a merge request and add review comments.

        Args:
            project_id: GitLab project ID
            mr_iid: Merge request internal ID
        """
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        changes = mr.changes()

        all_comments = []
        for strategy in self.strategies:
            comments = strategy.review_changes(changes["changes"])
            all_comments.extend(comments)

        self._add_review_comments(mr, all_comments)

    def _get_merge_request_changes(
        self, merge_request: Any
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get changes from a merge request.

        Args:
            merge_request: GitLab merge request object
        Returns:
            Dictionary containing merge request changes
        """
        changes = merge_request.changes()
        return {
            "changes": [
                {
                    "new_path": change["new_path"],
                    "diff": change["diff"],
                    "new_line": change.get("new_line", 1),
                }
                for change in changes["changes"]
            ]
        }

    def _add_review_comments(
        self, merge_request: Any, comments: List[ReviewComment]
    ) -> None:
        """Add review comments to a merge request.

        Args:
            merge_request: GitLab merge request object
            comments: List of review comments to add
        """
        for comment in comments:
            merge_request.discussions.create(
                {
                    "body": comment.content,
                    "position": {
                        "position_type": "text",
                        "new_path": comment.path,
                        "new_line": comment.line,
                    },
                }
            )
