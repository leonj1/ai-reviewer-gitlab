import os
from typing import List
from openai import OpenAI
from review_strategies import ReviewComment

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def analyze_changes(self, file_change: dict) -> List[ReviewComment]:
        prompt = self._create_review_prompt(file_change)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a code reviewer. Analyze the code changes and provide specific, actionable feedback."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Process the response and convert to ReviewComment objects
        return [
            ReviewComment(
                path=file_change['path'],
                line=file_change['line'],
                content=response.choices[0].message.content
            )
        ]
    
    def _create_review_prompt(self, file_change: dict) -> str:
        return f"""
        Please review the following code changes:
        
        File: {file_change['path']}
        Diff:
        {file_change['diff']}
        
        Provide specific feedback focusing on:
        1. Code quality
        2. Potential bugs
        3. Performance issues
        4. Best practices
        """
