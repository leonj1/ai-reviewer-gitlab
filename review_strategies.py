from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re


@dataclass
class ReviewComment:
    """A code review comment."""

    path: str
    line: int
    content: str
    suggestion: Optional[str] = None


class ReviewStrategy(ABC):
    """Base class for code review strategies."""

    @abstractmethod
    def review_changes(self, changes: List[Dict[str, Any]]) -> List[ReviewComment]:
        """Review code changes and return comments.

        Args:
            changes: List of code changes to review
        Returns:
            List of review comments
        """
        pass


class AIReviewStrategy(ReviewStrategy):
    """AI-powered code review strategy."""

    def __init__(self, llm_client: Any) -> None:
        """Initialize AI review strategy.

        Args:
            llm_client: LLM client for code analysis
        """
        self.llm_client = llm_client

    def review_changes(self, changes: List[Dict[str, Any]]) -> List[ReviewComment]:
        """Review code changes using AI.

        Args:
            changes: List of code changes to review
        Returns:
            List of review comments
        """
        return self.llm_client.analyze_code(changes)


class SecurityReviewStrategy(ReviewStrategy):
    """Security-focused code review strategy."""

    def __init__(self) -> None:
        """Initialize security review strategy."""
        self.patterns = {
            r"password\s*=": "Avoid hardcoding passwords",
            r"token\s*=": "Avoid hardcoding tokens",
            r"eval\(": "Avoid using eval() for security reasons",
            r"exec\(": "Avoid using exec() for security reasons",
        }

    def review_changes(self, changes: List[Dict[str, Any]]) -> List[ReviewComment]:
        """Review code changes for security issues.

        Args:
            changes: List of code changes to review
        Returns:
            List of review comments
        """
        comments = []
        for change in changes:
            for pattern, message in self.patterns.items():
                if re.search(pattern, change["diff"], re.IGNORECASE):
                    comments.append(
                        ReviewComment(
                            path=change["new_path"],
                            line=change.get("new_line", 1),
                            content=message,
                        )
                    )
        return comments
