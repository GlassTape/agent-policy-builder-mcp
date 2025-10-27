"""ICP Validator - Validates Simple ICP JSON structure."""

from typing import Any, Dict


class ICPValidator:
    """Validate Simple ICP structure"""
    
    def validate(self, icp: Dict[str, Any]) -> None:
        """
        Validate ICP structure.
        
        Args:
            icp: Simple ICP dictionary
            
        Raises:
            ValueError: If ICP is invalid
        """
        if not isinstance(icp, dict):
            raise ValueError("ICP must be a dictionary")
        
        # Check version
        if icp.get('version') != '1.0.0':
            raise ValueError("ICP version must be 1.0.0")
        
        # Check required sections
        if 'metadata' not in icp:
            raise ValueError("ICP must have 'metadata' section")
        if 'policy' not in icp:
            raise ValueError("ICP must have 'policy' section")
        if 'tests' not in icp:
            raise ValueError("ICP must have 'tests' section")
        
        # Validate metadata
        self._validate_metadata(icp['metadata'])
        
        # Validate policy
        self._validate_policy(icp['policy'])
        
        # Validate tests
        self._validate_tests(icp['tests'])
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate metadata section"""
        required_fields = ['name', 'description', 'resource']
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Metadata missing required field: {field}")
        
        # Name should be snake_case
        name = metadata['name']
        if not name.replace('_', '').isalnum():
            raise ValueError(f"Metadata name should be snake_case: {name}")
        
        # Compliance should be array if present
        if 'compliance' in metadata and not isinstance(metadata['compliance'], list):
            raise ValueError("Metadata compliance must be an array")
    
    def _validate_policy(self, policy: Dict[str, Any]) -> None:
        """Validate policy section"""
        if 'resource' not in policy:
            raise ValueError("Policy missing 'resource' field")
        if 'version' not in policy:
            raise ValueError("Policy missing 'version' field")
        if 'rules' not in policy:
            raise ValueError("Policy missing 'rules' field")
        
        rules = policy['rules']
        if not isinstance(rules, list) or len(rules) == 0:
            raise ValueError("Policy must have at least one rule")
        
        # Validate each rule
        for i, rule in enumerate(rules):
            self._validate_rule(rule, i)
        
        # Check for default deny rule
        last_rule = rules[-1]
        if last_rule.get('effect') != 'EFFECT_DENY' or '*' not in last_rule.get('actions', []):
            raise ValueError("Policy should end with a default deny rule")
    
    def _validate_rule(self, rule: Dict[str, Any], index: int) -> None:
        """Validate a single rule"""
        required_fields = ['actions', 'effect']
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Rule {index} missing required field: {field}")
        
        # Validate effect
        if rule['effect'] not in ['EFFECT_ALLOW', 'EFFECT_DENY']:
            raise ValueError(f"Rule {index} effect must be EFFECT_ALLOW or EFFECT_DENY")
        
        # Validate actions
        if not isinstance(rule['actions'], list) or len(rule['actions']) == 0:
            raise ValueError(f"Rule {index} actions must be a non-empty array")
        
        # Validate conditions if present
        if 'conditions' in rule:
            if not isinstance(rule['conditions'], list):
                raise ValueError(f"Rule {index} conditions must be an array")
    
    def _validate_tests(self, tests: list) -> None:
        """Validate tests section"""
        if not isinstance(tests, list):
            raise ValueError("Tests must be an array")
        
        if len(tests) < 2:
            raise ValueError("Must have at least 2 test cases (1 positive, 1 negative)")
        
        # Check for at least one positive and one negative test
        has_positive = any(t.get('category') == 'positive' for t in tests)
        has_negative = any(t.get('category') == 'negative' for t in tests)
        
        if not has_positive:
            raise ValueError("Must have at least one positive test case")
        if not has_negative:
            raise ValueError("Must have at least one negative test case")
        
        # Validate each test
        for i, test in enumerate(tests):
            self._validate_test(test, i)
    
    def _validate_test(self, test: Dict[str, Any], index: int) -> None:
        """Validate a single test case"""
        required_fields = ['name', 'category', 'input', 'expected']
        for field in required_fields:
            if field not in test:
                raise ValueError(f"Test {index} missing required field: {field}")
        
        # Validate category
        valid_categories = ['positive', 'negative', 'boundary', 'adversarial']
        if test['category'] not in valid_categories:
            raise ValueError(f"Test {index} category must be one of: {valid_categories}")
        
        # Validate expected
        if test['expected'] not in ['EFFECT_ALLOW', 'EFFECT_DENY']:
            raise ValueError(f"Test {index} expected must be EFFECT_ALLOW or EFFECT_DENY")
        
        # Validate input structure
        test_input = test['input']
        if 'principal' not in test_input:
            raise ValueError(f"Test {index} input missing 'principal'")
        if 'resource' not in test_input:
            raise ValueError(f"Test {index} input missing 'resource'")
        if 'actions' not in test_input:
            raise ValueError(f"Test {index} input missing 'actions'")

