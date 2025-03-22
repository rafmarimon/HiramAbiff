# Contributing to HiramAbiff

Thank you for your interest in contributing to HiramAbiff! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Environment Setup](#development-environment-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by the HiramAbiff Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

There are many ways to contribute to HiramAbiff:

### Reporting Bugs

- **Check if the bug has already been reported** by searching the project's issues.
- If the bug hasn't been reported, **open a new issue** with a clear title and detailed description.
- Include as much relevant information as possible: steps to reproduce, expected behavior, actual behavior, and environment details.

### Suggesting Enhancements

- **Check if the enhancement has already been suggested** by searching the project's issues.
- If it hasn't been suggested, **open a new issue** with a clear title and detailed description.
- Provide a clear and detailed explanation of what you want to happen and why it would be beneficial.

### Adding New Features

- **Discuss your idea first** by opening an issue before starting work on a new feature.
- This helps ensure your contribution aligns with the project's goals and that no one else is already working on something similar.

### Improving Documentation

- Documentation improvements are always welcome.
- Fix typos, clarify explanations, add examples, or create new guides.

### Writing Tests

- Help improve test coverage by adding missing tests.
- Fix existing tests that are flaky or incorrect.

## Development Environment Setup

To set up your development environment:

1. **Fork the repository** and clone it locally.

2. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   pip install -r requirements-dev.txt  # Installs development dependencies
   ```

3. **Set up environment variables** by copying `.env.example` to `.env` and filling in the required values.

4. **Run the dependency checker** to ensure everything is set up correctly:
   ```bash
   python tools/check_dependencies.py
   ```

5. **Run tests** to make sure everything works:
   ```bash
   pytest
   ```

## Pull Request Process

1. **Update your fork** to the latest code from the main repository.

2. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the coding standards.

4. **Add or update tests** as necessary.

5. **Update documentation** to reflect any changes.

6. **Run the tests** to ensure they pass:
   ```bash
   pytest
   ```

7. **Commit your changes** with a clear and descriptive commit message.

8. **Push your branch** to your fork.

9. **Submit a pull request** to the main repository.

10. **Respond to feedback** from reviewers and make necessary changes.

## Coding Standards

We follow PEP 8 for Python code style with a few modifications:

- **Line length**: Maximum 100 characters
- **Docstrings**: Follow the Google style for docstrings
- **Type annotations**: Use type annotations where appropriate
- **Imports**: Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library-specific imports

We use `black` and `isort` to automatically format code:

```bash
black .
isort .
```

And `flake8` to check for issues:

```bash
flake8 .
```

## Testing Guidelines

- All new features should include tests.
- Tests should be written using pytest.
- Tests should be placed in the `tests/` directory, mirroring the structure of the `src/` directory.
- Tests should be independent and have no side effects.
- Use mocking for external dependencies.

To run tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=hiramabiff

# Run specific tests
pytest tests/path/to/test_file.py
```

## Documentation

- All modules, classes, and functions should have docstrings.
- Follow the Google style for docstrings.
- Keep documentation up to date with code changes.
- Add examples where appropriate.

## Additional Resources

- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/) 