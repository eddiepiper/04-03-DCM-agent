# Contributing to DCM

Thank you for your interest in contributing to the Dynamic Capital Management (DCM) system! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/dcm.git
   cd dcm
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
5. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
6. Update the `.env` file with your configuration

## Code Style

We use several tools to maintain code quality:

- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

Before committing, run:
```bash
black .
flake8
mypy .
```

## Testing

We use `pytest` for testing. The test suite includes:
- Unit tests
- Integration tests
- End-to-end tests

Run tests with:
```bash
pytest
```

For coverage report:
```bash
pytest --cov
```

## Project Structure

```
dcm/
├── agents/              # AI agent implementations
├── data/               # Data management modules
├── dcm/                # Core DCM functionality
├── interface/          # User interface components
├── tests/              # Test suite
│   ├── agents/        # Agent tests
│   ├── dcm/           # Core functionality tests
│   └── integration/   # Integration tests
└── docs/              # Documentation
```

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests and code quality checks
4. Commit your changes:
   ```bash
   git commit -m "Description of your changes"
   ```
5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Create a Pull Request

## Commit Messages

Follow these guidelines for commit messages:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Documentation

- Update the README.md if needed
- Add docstrings to new functions and classes
- Update API documentation if you modify interfaces
- Add comments for complex logic

## Code Review Process

1. All pull requests require at least one review
2. Address review comments promptly
3. Keep pull requests focused and small
4. Update documentation as needed

## Release Process

1. Update version in setup.py
2. Update CHANGELOG.md
3. Create a release tag
4. Build and publish to PyPI

## Getting Help

- Open an issue for bugs or feature requests
- Join our community chat
- Check the documentation

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License. 