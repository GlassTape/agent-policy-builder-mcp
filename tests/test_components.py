"""Test core components."""

import pytest
from glasstape_policy_builder.icp_validator import ICPValidator
from glasstape_policy_builder.cerbos_generator import CerbosGenerator
from glasstape_policy_builder.templates import TemplateLibrary


def test_icp_validator():
    """Test ICP validation."""
    validator = ICPValidator()
    
    valid_icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "test_policy",
            "description": "Test policy",
            "resource": "test"
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
    
    # Should not raise exception
    validator.validate(valid_icp)


def test_icp_validator_invalid():
    """Test ICP validation with invalid data."""
    validator = ICPValidator()
    
    invalid_icp = {"invalid": "data"}
    
    with pytest.raises(ValueError):
        validator.validate(invalid_icp)


def test_cerbos_generator():
    """Test Cerbos YAML generation."""
    generator = CerbosGenerator()
    
    icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "test_policy",
            "description": "Test policy",
            "resource": "test"
        },
        "policy": {
            "resource": "test",
            "version": "1.0.0",
            "rules": [
                {
                    "actions": ["read"],
                    "effect": "EFFECT_ALLOW",
                    "conditions": ["request.resource.attr.public == true"]
                }
            ]
        },
        "tests": [
            {
                "name": "allow_public_read",
                "category": "positive",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "doc", "attr": {"public": True}},
                    "actions": ["read"]
                },
                "expected": "EFFECT_ALLOW"
            }
        ]
    }
    
    policy_yaml = generator.generate_policy(icp)
    test_yaml = generator.generate_tests(icp)
    
    assert "apiVersion: api.cerbos.dev/v1" in policy_yaml
    assert "EFFECT_ALLOW" in policy_yaml
    assert "request.resource.attr.public == true" in policy_yaml
    
    assert "allow_public_read" in test_yaml
    assert "EFFECT_ALLOW" in test_yaml


def test_template_library():
    """Test template library."""
    library = TemplateLibrary()
    
    # Test listing all templates
    templates = library.list_templates()
    assert len(templates) == 5
    
    # Test filtering by category
    finance_templates = library.list_templates("finance")
    assert len(finance_templates) == 1
    assert finance_templates[0].name == "Payment Execution"
    
    # Test getting categories
    categories = library.get_categories()
    assert "finance" in categories
    assert "healthcare" in categories
    
    # Test getting specific template
    template = library.get_template("payment_execution")
    assert template is not None
    assert template.name == "Payment Execution"
    
    # Test non-existent template
    template = library.get_template("non_existent")
    assert template is None