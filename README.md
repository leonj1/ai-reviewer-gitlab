# GitLab AI Code Reviewer

![GitLab AI Code Reviewer](ai-reviewer-gitlab.jpg)

An AI-powered code review tool that automatically analyzes GitLab merge requests and provides intelligent feedback using OpenAI's GPT models.

## Features

- Automated code review for GitLab merge requests
- Intelligent feedback using OpenAI's GPT models
- Multiple review strategies (Standard and Security)
- Type-safe Python implementation
- Comprehensive test coverage

## GitLab Integration Setup

1. Create a GitLab Bot Account (recommended):
   - Create a new GitLab account for the bot
   - This account will be used to post review comments on merge requests

2. Create a GitLab Access Token:
   - Go to Settings > Access Tokens in your GitLab instance
   - Create a new token with the following permissions:
     - `api` (API access)
     - `read_user` (Read user information)
     - `read_repository` (Read repository)
     - `write_discussion` (Post comments)
   - Save the token securely, you'll need it for configuration

3. Configure Webhook (Optional - for automatic reviews):
   - Go to your project's Settings > Webhooks
   - Add a new webhook with the following settings:
     - URL: Your deployed reviewer endpoint
     - Trigger: Merge request events
     - SSL verification: According to your setup
   - The reviewer will automatically analyze new merge requests and changes

4. Configure Project-level Variables:
   - Go to Settings > CI/CD > Variables
   - Add the following variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `GITLAB_TOKEN`: The access token created earlier
     - Mark them as Protected and Masked for security

## Local Development

### Prerequisites

- Python 3.11 or higher
- GitLab account and API token
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-reviewer-gitlab
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Set the following environment variables:

```bash
export GITLAB_URL="your-gitlab-instance-url"
export GITLAB_TOKEN="your-gitlab-api-token"
export OPENAI_API_KEY="your-openai-api-key"
```

### Usage

Run the main script to start reviewing merge requests:

```bash
python main.py
```

### Running Tests

#### Local Testing

Run tests using pytest:
```bash
# Run all tests with coverage
pytest --cov=. --cov-report=term-missing -v tests/

# Run specific test file
pytest tests/test_file_name.py -v
```

#### Docker Testing Environment

Build and run tests in a Docker container:
```bash
# Using make
make test

# Or manually
docker build -t gitlab-reviewer-test -f Dockerfile.test .
docker run --rm gitlab-reviewer-test
```

#### Project Structure

- `gitlab_reviewer.py`: Main GitLab integration logic
- `llm_client.py`: OpenAI API client implementation
- `review_strategies.py`: Different code review strategies
- `main.py`: Entry point of the application
- `tests/`: Test suite directory
