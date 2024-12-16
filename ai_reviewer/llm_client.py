from typing import Any, Dict, List, TypedDict
import openai
from review_strategies import ReviewComment


class ChatMessage(TypedDict):
    """Type for chat message."""

    role: str
    content: str


class LLMClient:
    """Client for interacting with OpenAI's API."""

    def __init__(self, api_key: str):
        """Initialize the LLM client with API key."""
        self.client = openai.OpenAI(api_key=api_key)

    def analyze_code(self, code_changes: List[Dict[str, Any]]) -> List[ReviewComment]:
        """
        Analyze code changes using OpenAI's API and return review comments.
        Args:
            code_changes: List of dictionaries containing code change information
        Returns:
            List of ReviewComment objects with suggestions
        """
        messages = self._prepare_messages(code_changes)
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            return self._parse_response(response, code_changes)
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return []

    def _prepare_messages(
        self, code_changes: List[Dict[str, Any]]
    ) -> List[ChatMessage]:
        """Prepare messages for the OpenAI API."""
        system_msg: ChatMessage = {
            "role": "system",
            "content": "You are a helpful code reviewer. Provide concise feedback.",
        }
        user_msgs: List[ChatMessage] = []
        for change in code_changes:
            path = change["new_path"]
            diff = change["diff"]
            msg: ChatMessage = {
                "role": "user",
                "content": f"Review this code change in {path}:\n{diff}",
            }
            user_msgs.append(msg)
        return [system_msg] + user_msgs

    def _parse_response(
        self, response: Any, code_changes: List[Dict[str, Any]]
    ) -> List[ReviewComment]:
        """Parse OpenAI API response into ReviewComment objects."""
        comments: List[ReviewComment] = []
        if not hasattr(response, "choices"):
            return comments

        for idx, choice in enumerate(response.choices):
            if idx < len(code_changes):
                comments.append(
                    ReviewComment(
                        path=code_changes[idx]["new_path"],
                        line=code_changes[idx]["line"],
                        content=choice.message["content"].strip(),
                    )
                )
        return comments
