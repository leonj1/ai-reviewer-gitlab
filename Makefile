.PHONY: test clean

# Docker image name
IMAGE_NAME := gitlab-reviewer-test

# Default target
.DEFAULT_GOAL := test

# Clean up docker images and cache
clean:
	@echo "🧹 Cleaning up..."
	docker rmi $(IMAGE_NAME) 2>/dev/null || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ 2>/dev/null || true

# Run tests in Docker container
test: clean
	@echo "🏗️  Building test container..."
	docker build -t $(IMAGE_NAME) -f Dockerfile.test .
	@echo "🧪 Running tests..."
	docker run --rm $(IMAGE_NAME)
