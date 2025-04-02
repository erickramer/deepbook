# DeepBook Test Suite

This directory contains tests for the DeepBook application.

## Running Tests

You can run the tests using the following commands:

```bash
# Run all tests
make test

# Run tests with coverage report
make coverage
```

## Test Structure

- `test_models.py`: Tests for data models and story generation
- `test_layout.py`: Tests for the Streamlit UI layout
- `test_prompts.py`: Tests for prompt templates
- `test_app.py`: Integration tests for the application workflow
- `conftest.py`: Pytest fixtures and configuration

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Create a new test file with the prefix `test_` if you're adding tests for a new module
2. Use appropriate unittest assertions for validation
3. Use mocks to avoid actual API calls
4. Update the `conftest.py` file if you need to add new fixtures

## Coverage Goals

We aim to maintain test coverage of at least 80% for the codebase. The coverage report will show which parts of the code are not being tested.