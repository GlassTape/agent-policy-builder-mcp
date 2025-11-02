"""Test policy tool - Run cerbos test on policy and test suite."""

import json
from typing import Dict, Any

from ..cerbos_cli import CerbosCLI
from .shared_utils import format_error


async def test_policy_tool(args: Dict[str, Any]) -> str:
    """
    Run cerbos test on provided policy and test suite.
    
    Args:
        policy_yaml: Cerbos policy YAML content
        test_yaml: Test suite YAML content
        
    Returns:
        JSON string with test results
    """
    try:
        policy_yaml = args.get("policy_yaml")
        test_yaml = args.get("test_yaml")
        
        if not policy_yaml:
            return format_error("policy_yaml is required")
        
        if not test_yaml:
            return format_error("test_yaml is required")
        
        # Initialize Cerbos CLI
        cerbos_cli = CerbosCLI()
        if not cerbos_cli.check_installation():
            return format_error("Cerbos CLI not installed. Install with: brew install cerbos/tap/cerbos")
        
        # Run cerbos test
        result = cerbos_cli.test(policy_yaml, test_yaml)
        
        # Format results
        status = "passed" if result.failed == 0 else "failed"
        
        return json.dumps({
            "status": status,
            "summary": {
                "passed": result.passed,
                "failed": result.failed,
                "total": result.total
            },
            "details": result.details
        }, indent=2)
                
    except Exception as e:
        return format_error(f"Test execution failed: {str(e)}")