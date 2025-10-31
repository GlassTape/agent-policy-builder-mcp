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
        try:
            policy = {
                'apiVersion': 'api.cerbos.dev/v1',
                'description': icp['metadata']['description'],
                'resourcePolicy': {
                    'version': icp['policy']['version'],
                    'resource': icp['policy']['resource'],
                    'rules': [self._transform_rule(rule, icp) for rule in icp['policy']['rules']]
                }
            }
            
            return yaml.dump(policy, default_flow_style=False, sort_keys=False)
        except KeyError as e:
            raise ValueError(f"Missing required field in ICP: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate policy YAML: {e}")
    
    def generate_tests(self, icp: Dict[str, Any]) -> str:
        """
        Convert ICP tests to Cerbos test YAML
        
        Args:
            icp: Simple ICP dictionary
            
        Returns:
            Cerbos test YAML string
        """
        try:
            test_suite = {
                'name': f"{icp['metadata']['name']}_test_suite",
                'description': f"Test suite for {icp['metadata']['name']}",
                'tests': [self._transform_test(test, icp) for test in icp['tests']]
            }
            
            return yaml.dump(test_suite, default_flow_style=False, sort_keys=False)
        except KeyError as e:
            raise ValueError(f"Missing required field in ICP: {e}")
        except Exception as e:
            raise ValueError(f"Failed to generate test YAML: {e}")
    
    def _transform_rule(self, rule: Dict[str, Any], icp: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform ICP rule to Cerbos rule"""
        try:
            cerbos_rule = {
                'actions': rule['actions'],
                'effect': rule['effect']
            }
            
            # Add roles if specified
            if rule.get('roles'):
                cerbos_rule['roles'] = rule['roles']
            
            # Build conditions including topic-based rules
            conditions = list(rule.get('conditions', []))
            
            # Add topic conditions from metadata
            if icp and 'metadata' in icp:
                metadata = icp['metadata']
                
                # Add allowed topics condition
                if metadata.get('topics'):
                    topics_condition = self._build_topics_condition(metadata['topics'], 'allow')
                    conditions.append(topics_condition)
                
                # Add blocked topics condition
                if metadata.get('blocked_topics'):
                    blocked_condition = self._build_topics_condition(metadata['blocked_topics'], 'block')
                    conditions.append(blocked_condition)
            
            # Add conditions if any exist
            if conditions:
                cerbos_rule['condition'] = {
                    'match': {
                        'expr': self._build_expr(conditions)
                    }
                }
            
            return cerbos_rule
        except KeyError as e:
            raise ValueError(f"Missing required field in rule: {e}")
    
    def _transform_test(self, test: Dict[str, Any], icp: Dict[str, Any]) -> Dict[str, Any]:
        """Transform ICP test to Cerbos test"""
        try:
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
        except KeyError as e:
            raise ValueError(f"Missing required field in test: {e}")
    
    def _build_expr(self, conditions: list[str]) -> str:
        """Build CEL expression from conditions"""
        # Join conditions with AND, wrapping each in parentheses
        return ' && '.join(f'({c})' for c in conditions)
    
    def _build_topics_condition(self, topics: list[str], mode: str) -> str:
        """Build topic-based condition."""
        if mode == 'allow':
            # At least one allowed topic must be present
            topic_checks = [f"'{topic}' in request.resource.attr.topics" for topic in topics]
            return f"({' || '.join(topic_checks)})"
        elif mode == 'block':
            # No blocked topics should be present
            topic_checks = [f"!('{topic}' in request.resource.attr.topics)" for topic in topics]
            return f"({' && '.join(topic_checks)})"
        else:
            raise ValueError(f"Invalid topic condition mode: {mode}")

