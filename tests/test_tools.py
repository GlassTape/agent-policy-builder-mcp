"""Test MCP tools."""

import pytest
from glasstape_policy_builder.tools.generate_policy import generate_policy_tool
from glasstape_policy_builder.tools.list_templates import list_templates_tool
from glasstape_policy_builder.tools.validate_policy import validate_policy_tool
from glasstape_policy_builder.tools.suggest_improvements import suggest_improvements_tool


@pytest.mark.asyncio
async def test_generate_policy():
    """Test policy generation."""
    icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "test_policy",
            "description": "Test policy for validation",
            "resource": "test",
            "safety_category": "G"
        },
        "policy": {
            "resource": "test",
            "version": "1.0.0",
            "rules": [
                {
                    "actions": ["read"],
                    "effect": "EFFECT_ALLOW",
                    "conditions": []
                },
                {
                    "actions": ["*"],
                    "effect": "EFFECT_DENY",
                    "conditions": []
                }
            ]
        },
        "tests": [
            {
                "name": "allow_read",
                "category": "positive",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "doc", "attr": {}},
                    "actions": ["read"]
                },
                "expected": "EFFECT_ALLOW"
            },
            {
                "name": "deny_write",
                "category": "negative",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "doc", "attr": {}},
                    "actions": ["write"]
                },
                "expected": "EFFECT_DENY"
            }
        ]
    }
    
    result = await generate_policy_tool({"icp": icp})
    assert "apiVersion: api.cerbos.dev/v1" in result
    assert "EFFECT_ALLOW" in result
    assert "test_policy" in result


@pytest.mark.asyncio
async def test_generate_policy_missing_icp():
    """Test policy generation with missing ICP."""
    result = await generate_policy_tool({})
    assert "Generate Policy" in result  # Returns usage guidance


@pytest.mark.asyncio
async def test_list_templates():
    """Test template listing."""
    result = await list_templates_tool({})
    assert "Policy Templates" in result
    assert "Payment Execution" in result


@pytest.mark.asyncio
async def test_list_templates_by_category():
    """Test template listing by category."""
    result = await list_templates_tool({"category": "finance"})
    assert "Payment Execution" in result


@pytest.mark.asyncio
async def test_validate_policy():
    """Test policy validation."""
    policy_yaml = """
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: test
  version: "1.0.0"
  rules:
    - actions: ["read"]
      effect: EFFECT_ALLOW
"""
    result = await validate_policy_tool({"policy_yaml": policy_yaml})
    assert "Policy Validation" in result


@pytest.mark.asyncio
async def test_suggest_improvements():
    """Test security analysis."""
    policy_yaml = """
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: test
  rules:
    - actions: ["read"]
      effect: EFFECT_ALLOW
      condition:
        match:
          expr: "true"
    - actions: ["*"]
      effect: EFFECT_DENY
"""
    result = await suggest_improvements_tool({"policy_yaml": policy_yaml})
    assert "Security Analysis" in result
    assert "checks passed" in result


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in tools."""
    # Test invalid ICP
    invalid_icp = {"invalid": "data"}
    result = await generate_policy_tool({"icp": invalid_icp})
    assert "Error generating policy" in result
    
    # Test missing policy_yaml
    result = await validate_policy_tool({})
    assert "Error:" in result or "policy_yaml" in result
    
    # Test missing policy_yaml for suggestions
    result = await suggest_improvements_tool({})
    assert "Error: 'policy_yaml' parameter required" in result