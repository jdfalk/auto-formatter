# file: Makefile
# Auto Formatter Development Makefile

.PHONY: help install test lint format clean validate release

# Default target
help:
	@echo "Auto Formatter Development Commands:"
	@echo ""
	@echo "  install     Install development dependencies"
	@echo "  test        Run test suite"
	@echo "  lint        Run linting checks"
	@echo "  format      Format all code"
	@echo "  validate    Validate action.yml"
	@echo "  clean       Clean up temporary files"
	@echo "  release     Prepare for release"
	@echo "  help        Show this help message"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements-dev.txt
	@echo "Installing Node.js dependencies..."
	npm install
	@echo "Installing pre-commit hooks..."
	pre-commit install || echo "pre-commit not available"

# Run tests
test:
	@echo "Running Python tests..."
	python -m pytest test/ -v --cov=scripts --cov-report=html --cov-report=term
	@echo "Testing action locally..."
	act pull_request -j format --dryrun || echo "Act not available, skipping local action test"

# Run linting
lint:
	@echo "Linting Python code..."
	ruff check scripts/ test/
	@echo "Linting with mypy..."
	mypy scripts/ --ignore-missing-imports
	@echo "Security check with bandit..."
	bandit -r scripts/ -f json -o bandit-report.json || true
	@echo "Linting JavaScript/JSON..."
	npx eslint . --ext .js,.json
	@echo "Checking action.yml..."
	npx action-validator action.yml || echo "Action validator not available"

# Format code
format:
	@echo "Formatting Python code..."
	ruff format scripts/ test/
	isort scripts/ test/
	@echo "Formatting JavaScript/JSON..."
	npx prettier --write .
	@echo "Formatting complete!"

# Validate action
validate:
	@echo "Validating action.yml structure..."
	npx action-validator action.yml
	@echo "Testing action inputs..."
	@echo "Action validation complete!"

# Clean up
clean:
	@echo "Cleaning up temporary files..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.log
	rm -rf bandit-report.json
	rm -rf safety-report.json
	rm -rf node_modules/.cache/
	@echo "Cleanup complete!"

# Prepare for release
release: clean format lint test validate
	@echo "Release preparation complete!"
	@echo "Ready to create release. Update version numbers and create tag."
	@echo ""
	@echo "Next steps:"
	@echo "1. Update version in action.yml"
	@echo "2. Update version in package.json"
	@echo "3. Update CHANGELOG.md"
	@echo "4. Commit changes: git add . && git commit -m 'chore: prepare release vX.Y.Z'"
	@echo "5. Create tag: git tag -a vX.Y.Z -m 'Release vX.Y.Z'"
	@echo "6. Push: git push origin main --tags"

# Development server (if needed)
dev:
	@echo "Starting development environment..."
	@echo "Use 'make test' to run tests in watch mode"
	@echo "Use 'make format' to format code"
	@echo "Use 'make lint' to check code quality"

# Quick check before commit
check: format lint
	@echo "Pre-commit checks complete!"

# Update dependencies
update:
	@echo "Updating Python dependencies..."
	pip install --upgrade -r requirements-dev.txt
	@echo "Updating Node.js dependencies..."
	npm update
	@echo "Dependencies updated!"
