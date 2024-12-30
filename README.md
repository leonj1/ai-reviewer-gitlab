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

3. Configure Project-level Variables:
   - Go to Settings > CI/CD > Variables
   - Add the following variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `GITLAB_TOKEN`: The access token created earlier
     - Mark them as Protected and Masked for security

## Using the Reviewer in Your Project

### Step 1: Add Required Variables
In the project you want to be reviewed, go to Settings > CI/CD > Variables and add:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GITLAB_TOKEN`: The GitLab access token from setup step 2
Mark both as Protected and Masked for security.

### Step 2: Create GitLab CI Configuration
Add this configuration to your project's `.gitlab-ci.yml`:

```yaml
ai-review:
  image: python:3.11-slim
  variables:
    GIT_STRATEGY: clone
  script:
    - pip install git+https://gitlab.com/leonj2-pub/ai-reviewer-gitlab.git#egg=ai-reviewer-gitlab
    - python -m ai_reviewer
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### Step 3: Configure Review Settings (Optional)
Create `.ai-reviewer.yml` in your project root to customize the review:

```yaml
review_strategies:
  - standard  # Basic code review
  - security  # Security-focused review

# Optional settings
settings:
  max_files_per_review: 10
  excluded_files:
    - "*.md"
    - "*.txt"
  review_comment_prefix: "🤖 AI Review:"
```

The reviewer will now automatically run on all merge requests and add comments based on the AI analysis.

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

4. Set up git hooks:
```bash
make setup
```

This will configure git to use the project's hooks, which include:
- A pre-push hook that runs tests before allowing a push to proceed

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
- `.githooks/`: Git hooks for development workflow
  - `pre-push`: Runs tests before allowing a push
