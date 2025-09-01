# Contributing to Agenora

Thank you for your interest in contributing to Agenora! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue tracker to avoid duplicates. When you create a bug report, include:

1. A clear and descriptive title
2. Steps to reproduce the problem
3. Expected behavior
4. Actual behavior
5. Screenshots or code snippets if applicable
6. Environment details (OS, Python version, installed packages)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

1. A clear and descriptive title
2. Step-by-step description of the suggested enhancement
3. Description of the current behavior and the expected behavior
4. Explanation of why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Add or update tests as needed
5. Update documentation to reflect your changes
6. Run the test suite to ensure nothing is broken
7. Commit your changes (`git commit -m 'Add some feature'`)
8. Push to your branch (`git push origin feature/your-feature`)
9. Open a Pull Request

## Development Setup

1. Clone your fork of the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Project Structure

```
agenora/
├── backend/               # Backend Python package
│   ├── agenora/           # Main package
│   │   ├── api/           # API layer
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database layer
│   │   ├── agent_manager/ # Agent management
│   │   └── llm_manager/   # LLM provider integrations
│   └── tests/             # Backend tests
├── frontend/              # React frontend
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## Coding Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints wherever possible
- Write docstrings for all functions, classes, and modules
- Keep line length to a maximum of 88 characters
- Use meaningful variable and function names

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Run tests with pytest:
  ```bash
  pytest
  ```

## Documentation

- Update documentation for all new features
- Use clear and concise language
- Include examples when helpful
- Follow Markdown best practices

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## Licensing

By contributing to Agenora, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions, please create an issue with the label "question" or reach out to the project maintainers.

Thank you for contributing to Agenora!
