# Contributing to GlassTape Policy Builder

Thank you for your interest in contributing! This project helps developers generate secure Cerbos policies via MCP.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/glasstape/glasstape-policy-builder-mcp.git
cd glasstape-policy-builder-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
```

## Development Guidelines

- **Code Style**: Use Black formatter and Ruff linter
- **Type Hints**: Required for all functions
- **Tests**: Add tests for new features
- **Documentation**: Update docstrings and README

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## Reporting Issues

Use GitHub Issues for:
- Bug reports
- Feature requests
- Documentation improvements

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## License

By contributing, you agree your contributions will be licensed under Apache 2.0.