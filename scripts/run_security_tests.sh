#!/bin/bash

# Run security tests
echo "Running security tests..."

# Run pytest with security tests
pytest tests/security/ -v --cov=app --cov-report=term-missing

# Run bandit for Python security checks
echo "Running bandit security checks..."
bandit -r app/

# Run safety for dependency checks
echo "Running safety checks..."
safety check

# Run mypy for type checking
echo "Running mypy type checks..."
mypy app/

# Run black for code formatting
echo "Running black code formatting check..."
black --check app/

# Run isort for import sorting
echo "Running isort import sorting check..."
isort --check-only app/

# Run flake8 for linting
echo "Running flake8 linting..."
flake8 app/

echo "Security tests completed!" 