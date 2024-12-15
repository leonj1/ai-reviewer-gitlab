import os
from typing import List
import gitlab
from dotenv import load_dotenv

from review_strategies import ReviewStrategy, ReviewComment

class GitLabReviewer:
    def __init__(self, strategies: List[ReviewStrategy]):
        load_dotenv()
        self.gl = gitlab.Gitlab(
            url=os.getenv('GITLAB_URL'),
            private_token=os.getenv('GITLAB_TOKEN')
        )
        self.strategies = strategies
    
    def process_merge_request(self, project_id: int, mr_iid: int) -> None:
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        changes = self._get_merge_request_changes(mr)
        all_comments = []
        
        for strategy in self.strategies:
            comments = strategy.review_changes(changes)
            all_comments.extend(comments)
        
        self._submit_review(mr, all_comments)
    
    def _get_merge_request_changes(self, mr) -> dict:
        changes = mr.changes()
        return {
            'changes': [
                {
                    'path': change['new_path'],
                    'diff': change['diff'],
                    'line': 1  # Simplified for example
                }
                for change in changes['changes']
            ]
        }
    
    def _submit_review(self, mr, comments: List[ReviewComment]) -> None:
        for comment in comments:
            mr.discussions.create({
                'body': comment.content,
                'position': {
                    'position_type': 'text',
                    'new_path': comment.path,
                    'new_line': comment.line
                }
            })
