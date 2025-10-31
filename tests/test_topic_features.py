"""Test topic-aware features."""

import pytest
from glasstape_policy_builder.topic_taxonomy import taxonomy, TopicTaxonomy, SafetyCategory
from glasstape_policy_builder.icp_validator import ICPValidator
from glasstape_policy_builder.cerbos_generator import CerbosGenerator


def test_topic_taxonomy():
    """Test topic taxonomy functionality."""
    # Test getting all topics
    all_topics = taxonomy.get_all_topics()
    assert "payment" in all_topics
    assert "pii" in all_topics
    assert "recipe" in all_topics
    
    # Test category topics
    financial_topics = taxonomy.get_category_topics("financial")
    assert "payment" in financial_topics
    assert "transaction" in financial_topics
    
    # Test topic validation
    validation = taxonomy.validate_topics(["payment", "pii", "invalid_topic"])
    assert "payment" in validation["valid"]
    assert "pii" in validation["valid"]
    assert "invalid_topic" in validation["invalid"]
    assert "financial" in validation["categories"]
    assert "privacy" in validation["categories"]
    
    # Test safety level determination
    safety_level = taxonomy.get_safety_level(["payment", "adult"])
    assert safety_level == SafetyCategory.R  # Should be highest level


def test_topic_aware_icp_validation():
    """Test ICP validation with topics."""
    validator = ICPValidator()
    
    # Valid ICP with topics
    valid_icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "topic_aware_policy",
            "description": "Test policy with topics",
            "resource": "test",
            "topics": ["payment", "pii"],
            "blocked_topics": ["recipe", "adult"],
            "safety_category": "PG_13"
        },
        "policy": {
            "resource": "test",
            "version": "1.0.0",
            "rules": [
                {
                    "actions": ["execute"],
                    "effect": "EFFECT_ALLOW",
                    "conditions": ["request.resource.attr.amount <= 50"]
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
                "name": "allow_payment",
                "category": "positive",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "payment", "attr": {"topics": ["payment"], "amount": 30}},
                    "actions": ["execute"]
                },
                "expected": "EFFECT_ALLOW"
            },
            {
                "name": "block_recipe",
                "category": "negative",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "request", "attr": {"topics": ["recipe"]}},
                    "actions": ["execute"]
                },
                "expected": "EFFECT_DENY"
            }
        ]
    }
    
    # Should not raise exception
    validator.validate(valid_icp)


def test_topic_aware_icp_validation_invalid():
    """Test ICP validation with invalid topics."""
    validator = ICPValidator()
    
    # Invalid topics
    invalid_icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "invalid_topic_policy",
            "description": "Test policy with invalid topics",
            "resource": "test",
            "topics": ["invalid_topic", "another_invalid"]
        },
        "policy": {
            "resource": "test",
            "version": "1.0.0",
            "rules": [
                {"actions": ["*"], "effect": "EFFECT_DENY", "conditions": []}
            ]
        },
        "tests": [
            {
                "name": "test",
                "category": "positive",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "test", "attr": {}},
                    "actions": ["test"]
                },
                "expected": "EFFECT_ALLOW"
            }
        ]
    }
    
    with pytest.raises(ValueError, match="Invalid topics"):
        validator.validate(invalid_icp)


def test_topic_aware_cerbos_generation():
    """Test Cerbos YAML generation with topics."""
    generator = CerbosGenerator()
    
    icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "payment_policy",
            "description": "Payment policy with topic controls",
            "resource": "payment",
            "topics": ["payment", "transaction"],
            "blocked_topics": ["recipe", "adult"]
        },
        "policy": {
            "resource": "payment",
            "version": "1.0.0",
            "rules": [
                {
                    "actions": ["execute"],
                    "effect": "EFFECT_ALLOW",
                    "conditions": ["request.resource.attr.amount <= 50"]
                },
                {
                    "actions": ["*"],
                    "effect": "EFFECT_DENY",
                    "conditions": []
                }
            ]
        },
        "tests": []
    }
    
    policy_yaml = generator.generate_policy(icp)
    
    # Check that topic conditions are included
    assert "'payment' in request.resource.attr.topics" in policy_yaml
    assert "'transaction' in request.resource.attr.topics" in policy_yaml
    assert "!('recipe' in request.resource.attr.topics)" in policy_yaml
    assert "!('adult' in request.resource.attr.topics)" in policy_yaml
    assert "request.resource.attr.amount <= 50" in policy_yaml


def test_topic_condition_building():
    """Test topic condition building logic."""
    generator = CerbosGenerator()
    
    # Test allow condition
    allow_condition = generator._build_topics_condition(["payment", "transaction"], "allow")
    expected_allow = "('payment' in request.resource.attr.topics || 'transaction' in request.resource.attr.topics)"
    assert allow_condition == expected_allow
    
    # Test block condition
    block_condition = generator._build_topics_condition(["recipe", "adult"], "block")
    expected_block = "(!('recipe' in request.resource.attr.topics) && !('adult' in request.resource.attr.topics))"
    assert block_condition == expected_block


def test_safety_category_validation():
    """Test safety category validation."""
    validator = ICPValidator()
    
    # Valid safety category
    valid_icp = {
        "version": "1.0.0",
        "metadata": {
            "name": "safe_policy",
            "description": "Policy with valid safety category",
            "resource": "test",
            "safety_category": "PG_13"
        },
        "policy": {
            "resource": "test",
            "version": "1.0.0",
            "rules": [{"actions": ["*"], "effect": "EFFECT_DENY", "conditions": []}]
        },
        "tests": [
            {
                "name": "test_positive",
                "category": "positive",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "test", "attr": {}},
                    "actions": ["test"]
                },
                "expected": "EFFECT_ALLOW"
            },
            {
                "name": "test_negative",
                "category": "negative",
                "input": {
                    "principal": {"id": "user", "roles": []},
                    "resource": {"id": "test", "attr": {}},
                    "actions": ["forbidden"]
                },
                "expected": "EFFECT_DENY"
            }
        ]
    }
    
    # Should not raise exception
    validator.validate(valid_icp)
    
    # Invalid safety category
    invalid_icp = valid_icp.copy()
    invalid_icp["metadata"]["safety_category"] = "INVALID"
    
    with pytest.raises(ValueError, match="Invalid safety_category"):
        validator.validate(invalid_icp)


def test_topic_taxonomy_guidance():
    """Test topic taxonomy guidance generation."""
    guidance = taxonomy.get_topic_guidance()
    
    assert "Topic Selection Guidelines" in guidance
    assert "payment" in guidance
    assert "pii" in guidance
    assert "Examples:" in guidance
    assert "Safety Categories:" in guidance


if __name__ == "__main__":
    pytest.main([__file__])