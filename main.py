from gitlab_reviewer import GitLabReviewer
from review_strategies import AIReviewStrategy, SecurityReviewStrategy
from llm_client import LLMClient

def main():
    # Initialize strategies
    llm_client = LLMClient()
    strategies = [
        AIReviewStrategy(llm_client),
        SecurityReviewStrategy()
    ]
    
    # Create reviewer
    reviewer = GitLabReviewer(strategies)
    
    # Process merge request
    project_id = 123  # Replace with actual project ID
    mr_iid = 456      # Replace with actual MR IID
    reviewer.process_merge_request(project_id, mr_iid)

if __name__ == "__main__":
    main()
