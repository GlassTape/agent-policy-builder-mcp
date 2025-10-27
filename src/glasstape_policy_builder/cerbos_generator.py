"""Cerbos YAML Generator - Converts Simple ICP to Cerbos YAML format."""

import yaml
from typing import Dict, Any


class CerbosGenerator:
    """Generate Cerbos YAML from Simple ICP"""
    
    def generate_policy(self, icp: Dict[str, Any]) -> str:
        """
        Convert ICP to Cerbos policy YAML
        
        Args:
            icp: Simple ICP dictionary
            
        Returns:
            Cerbos policy YAML string
        """
        policy = {
            'apiVersion': 'api.cerbos.dev/v1',
            'description': icp['metadata']['description'],
            'resourcePolicy': {
                'version': icp['policy']['version'],
                'resource': icp['policy']['resource'],
                'rules': [self._transform_rule(rule) for rule in icp['policy']['rules']]
            }
        }
        
        return yaml.dump(policy, default_flow_style=False, sort_keys=False)
    
    def generate_tests(self, icp: Dict[str, Any]) -> str:
        """
        Convert ICP tests to Cerbos test YAML
        
        Args:
            icp: Simple ICP dictionary
            
        Returns:
            Cerbos test YAML string
        """
        test_suite = {
            'name': f"{icp['metadata']['name']}_test_suite",
            'description': f"Test suite for {icp['metadata']['name']}",
            'tests': [self._transform_test(test, icp) for test in icp['tests']]
        }
        
        return yaml.dump(test_suite, default_flow_style=False, sort_keys=False)
    
    def _transform_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Transform ICP rule to Cerbos rule"""
        cerbos_rule = {
            'actions': rule['actions'],
            'effect': rule['effect']
        }
        
        # Add roles if specified
        if rule.get('roles'):
            cerbos_rule['roles'] = rule['roles']
        
        # Add conditions if specified
        if rule.get('conditions'):
            cerbos_rule['condition'] = {
                'match': {
                    'expr': self._build_expr(rule['conditions'])
                }
            }
        
        return cerbos_rule
    
    def _transform_test(self, test: Dict[str, Any], icp: Dict[str, Any]) -> Dict[str, Any]:
        """Transform ICP test to Cerbos test"""
        return {
            'name': test['name'],
            'input': {
                'principal': {
                    'id': test['input']['principal'].get('id', 'test-principal'),
                    'roles': test['input']['principal'].get('roles', [])
                },
                'resource': {
                    'kind': icp['policy']['resource'],
                    'id': test['input']['resource'].get('id', 'test-resource'),
                    'attr': test['input']['resource'].get('attr', {})
                },
                'actions': test['input']['actions']
            },
            'expected': [
                {
                    'action': action,
                    'effect': test['expected']
                }
                for action in test['input']['actions']
            ]
        }
    
    def _build_expr(self, conditions: list[str]) -> str:
        """Build CEL expression from conditions"""
        # Join conditions with AND, wrapping each in parentheses
        return ' && '.join(f'({c})' for c in conditions)

