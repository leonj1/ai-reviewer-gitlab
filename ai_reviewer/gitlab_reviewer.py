import os
import sys
import logging
from typing import List, Dict, Any
import gitlab

from .review_strategies import ReviewStrategy, ReviewComment

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitLabReviewer:
    """GitLab code reviewer that processes merge requests."""

    def __init__(self, strategies: List[ReviewStrategy]) -> None:
        """Initialize GitLab reviewer with review strategies.

        Args:
            strategies: List of review strategies to apply
        """
        self.strategies = strategies

        # Get GitLab configuration
        gitlab_url = os.getenv("CI_SERVER_URL") or os.getenv("GITLAB_URL")

        # Try CI_JOB_TOKEN first (for GitLab CI), fallback to GITLAB_TOKEN (for local dev)
        gitlab_token = os.getenv("CI_JOB_TOKEN") or os.getenv("GITLAB_TOKEN")

        if not gitlab_url or not gitlab_token:
            logger.error("Missing GitLab configuration:")
            if not gitlab_url:
                logger.error("- GITLAB_URL or CI_SERVER_URL not set")
            if not gitlab_token:
                logger.error("- Neither CI_JOB_TOKEN (for CI) nor GITLAB_TOKEN (for local) is set")
            sys.exit(1)

        logger.info(f"Connecting to GitLab at: {gitlab_url}")
        try:
            if os.getenv("CI_JOB_TOKEN"):
                logger.info("Using CI job token for authentication")
                self.gl = gitlab.Gitlab(url=gitlab_url, job_token=gitlab_token)
            else:
                logger.info("Using private token for authentication")
                self.gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_token)

            self.gl.auth()
            logger.info("Successfully authenticated with GitLab")
        except Exception as e:
            logger.error(f"Failed to connect to GitLab: {str(e)}")
            sys.exit(1)

    def process_merge_request(self, project_id: int, mr_iid: int) -> None:
        """Process a merge request and add review comments.

        Args:
            project_id: GitLab project ID
            mr_iid: Merge request internal ID
        """
        logger.info(f"Processing merge request {mr_iid} in project {project_id}")

        try:
            # Get project
            logger.info(f"Fetching project {project_id}")
            project = self.gl.projects.get(project_id)
            logger.info(f"Found project: {project.name}")

            # Get merge request
            logger.info(f"Fetching merge request {mr_iid}")
            mr = project.mergerequests.get(mr_iid)
            logger.info(f"Found merge request: {mr.title}")

            # Get changes
            logger.info("Fetching merge request changes")
            changes = self._get_merge_request_changes(mr)
            logger.info(f"Found {len(changes)} changed files")

            # Apply review strategies
            all_comments = []
            for strategy in self.strategies:
                logger.info(f"Applying review strategy: {strategy.__class__.__name__}")
                comments = strategy.review_changes(changes)
                logger.info(f"Strategy generated {len(comments)} comments")
                all_comments.extend(comments)

            # Add comments to merge request
            logger.info(f"Adding {len(all_comments)} review comments")
            self._add_review_comments(mr, all_comments)
            logger.info("Successfully added review comments")

        except gitlab.exceptions.GitlabError as e:
            logger.error(f"GitLab API error: {str(e)}")
            if hasattr(e, 'response_code'):
                logger.error(f"Response code: {e.response_code}")
            if hasattr(e, 'response_body'):
                logger.error(f"Response body: {e.response_body}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            sys.exit(1)

    def _get_merge_request_changes(self, mr: Any) -> List[Dict[str, Any]]:
        """Get changes from merge request.

        Args:
            mr: GitLab merge request object
        Returns:
            List of changes with file and diff information
        """
        logger.info("Fetching merge request changes")
        changes = mr.changes()['changes']
        processed_changes = []

        for change in changes:
            logger.debug(f"Processing change in file: {change.get('new_path')}")
            if 'diff' in change and change['diff']:
                processed_changes.append({
                    'new_path': change['new_path'],
                    'diff': change['diff'],
                    'line': 1  # Default to first line if not specified
                })

        return processed_changes

    def _add_review_comments(self, mr: Any, comments: List[ReviewComment]) -> None:
        """Add review comments to merge request.

        Args:
            mr: GitLab merge request object
            comments: List of review comments to add
        """
        for comment in comments:
            logger.info(f"Adding comment to {comment.path} at line {comment.line}")
            try:
                mr.discussions.create({
                    'body': comment.content,
                    'position': {
                        'position_type': 'text',
                        'new_path': comment.path,
                        'new_line': comment.line,
                    }
                })
            except Exception as e:
                logger.error(f"Failed to add comment: {str(e)}")
                # Continue with other comments even if one fails
