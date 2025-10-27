# 🧩 GlassTape Policy Builder MCP Server

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

> **Transform natural language into production-ready Cerbos policies via MCP**

An open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that converts natural language security requirements into validated **Cerbos YAML policies**. Designed for AI agent governance, policy-as-code workflows, and zero-trust security implementations.

## ✨ Features

- 🔒 **Secure by Default** - Air-gapped operation, no mandatory cloud dependencies
- ⚡ **Client-LLM Mode** - Works with any MCP client's LLM (Cursor, Claude, Q)
- 🎯 **Deterministic Generation** - Simple ICP JSON → validated Cerbos YAML
- 🧪 **Automated Validation** - Uses `cerbos compile` and `cerbos test` for verification
- 🛡️ **Security Analysis** - Built-in red-team checks and compliance mapping
- 🧩 **MCP Native** - Seamless IDE integration via Model Context Protocol
- 📚 **Template Library** - Pre-built patterns for finance, healthcare, AI safety

## 🚀 Quick Start

### 1. Prerequisites

**Install Cerbos CLI** (required for policy validation):

```bash
# macOS
brew install cerbos/tap/cerbos

# Linux
curl -L https://github.com/cerbos/cerbos/releases/latest/download/cerbos_Linux_x86_64 \
  -o /usr/local/bin/cerbos && chmod +x /usr/local/bin/cerbos

# Verify installation
cerbos version
```

### 2. Install the MCP Server

```bash
# Basic installation
pip install glasstape-policy-builder-mcp

# With optional LLM support (for server-side natural language parsing)
pip install glasstape-policy-builder-mcp[anthropic]  # Anthropic Claude
pip install glasstape-policy-builder-mcp[openai]     # OpenAI GPT
pip install glasstape-policy-builder-mcp[llm]        # All LLM providers

# Development installation
pip install glasstape-policy-builder-mcp[dev]
```

### 3. Configure Your MCP Client

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "glasstape-policy-builder": {
      "command": "glasstape-policy-builder-mcp"
    }
  }
}
```

**Cursor/Zed**: Add similar configuration in your IDE's MCP settings.

**Optional: Server-side LLM** (for natural language processing):

```json
{
  "mcpServers": {
    "glasstape-policy-builder": {
      "command": "glasstape-policy-builder-mcp",
      "env": {
        "LLM_PROVIDER": "anthropic",
        "ANTHROPIC_API_KEY": "sk-ant-your-key"
      }
    }
  }
}
```

### 4. Usage Examples

**Generate a Policy** (in Claude Desktop or MCP-enabled IDE):

```
Create a payment policy for AI agents:
- Allow payments up to $50
- Block sanctioned entities
- Limit to 5 transactions per 5 minutes
```

**List Available Templates**:

```
list_templates
```

**Validate a Policy**:

```
validate_policy with policy_yaml: "<your-cerbos-yaml>"
```

### 5. Troubleshooting

**Cerbos CLI not found**:
- Ensure Cerbos CLI is installed and in your PATH
- Run `cerbos version` to verify installation

**MCP server not connecting**:
- Check your MCP client configuration
- Restart your IDE after configuration changes
- Verify the command path is correct

**Policy validation fails**:
- Check YAML syntax in generated policy
- Ensure Cerbos CLI is working: `cerbos compile --help`
- Review error messages for specific issues

**Import errors**:
- Ensure you have Python 3.10 or higher
- Try reinstalling: `pip uninstall glasstape-policy-builder-mcp && pip install glasstape-policy-builder-mcp`

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `generate_policy` | Transform natural language → Cerbos YAML |
| `validate_policy` | Check policy syntax with `cerbos compile` |
| `test_policy` | Run test suites with `cerbos test` |
| `suggest_improvements` | Perform security analysis |
| `list_templates` | Browse built-in policy templates |

## 📋 Examples

Complete policy examples for all 5 template categories:

| Category | Example | Description |
|----------|---------|-------------|
| **Finance** | [payment_policy.md](examples/payment_policy.md) | Payment execution with limits |
| **Healthcare** | [phi_access_policy.md](examples/phi_access_policy.md) | HIPAA-compliant PHI access |
| **AI Safety** | [ai_model_invocation_policy.md](examples/ai_model_invocation_policy.md) | Model invocation with guardrails |
| **Data Access** | [pii_export_policy.md](examples/pii_export_policy.md) | GDPR-compliant PII export control |
| **System** | [admin_access_policy.md](examples/admin_access_policy.md) | Admin access with MFA |

### Quick Example

**Natural Language Input:**
```
Allow AI agents to execute payments up to $50. Block sanctioned entities.
```

**Generated Cerbos YAML:**
```yaml
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: payment
  rules:
    - actions: ["execute"]
      effect: EFFECT_ALLOW
      condition:
        match:
          expr: "request.resource.attr.amount <= 50"
    - actions: ["*"]
      effect: EFFECT_DENY
```

**Plus:** Automated test suite and security analysis.

See [examples/README.md](examples/README.md) for complete examples.

## 🏗️ Architecture

Simple ICP JSON → Cerbos YAML → Validation → Security Analysis

## 🧪 Development

```bash
# Clone and setup
git clone https://github.com/glasstape/glasstape-policy-builder-mcp.git
cd glasstape-policy-builder-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
```

## 📄 License

Apache 2.0