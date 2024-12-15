from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ReviewComment:
    path: str
    line: int
    content: str
    suggestion: Optional[str] = None

class ReviewStrategy(ABC):
    @abstractmethod
    def review_changes(self, diff_data: dict) -> List[ReviewComment]:
        pass

class AIReviewStrategy(ReviewStrategy):
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def review_changes(self, diff_data: dict) -> List[ReviewComment]:
        comments = []
        for file_change in diff_data['changes']:
            review = self.llm_client.analyze_changes(file_change)
            comments.extend(review)
        return comments

class SecurityReviewStrategy(ReviewStrategy):
    def review_changes(self, diff_data: dict) -> List[ReviewComment]:
        comments = []
        for file_change in diff_data['changes']:
            if self._contains_security_issues(file_change):
                comments.append(
                    ReviewComment(
                        path=file_change['path'],
                        line=file_change['line'],
                        content="Potential security issue detected"
                    )
                )
        return comments
    
    def _contains_security_issues(self, file_change: dict) -> bool:
        # Implementation for security checks
        return False
