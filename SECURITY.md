# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: security@glasstape.ai

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You should receive a response within 48 hours. We will keep you informed of the progress.

## Security Features

- **Air-gap capable**: No mandatory cloud dependencies
- **Input validation**: All user inputs are validated
- **Secure defaults**: Policies require explicit allow rules
- **Local execution**: Cerbos CLI runs locally

## Best Practices

When using this tool:
- Keep Cerbos CLI updated
- Validate generated policies before deployment
- Review security analysis suggestions
- Use client-LLM mode for maximum security