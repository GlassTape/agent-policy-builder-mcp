"""Test policy tool implementation."""

from typing import Dict, Any

from ..cerbos_cli import CerbosCLI


async def test_policy_tool(args: Dict[str, Any]) -> str:
    """Run tests against policy using cerbos test."""
    policy_yaml = args.get("policy_yaml", "")
    test_yaml = args.get("test_yaml", "")
    
    if not policy_yaml or not test_yaml:
        return "Error: Both 'policy_yaml' and 'test_yaml' parameters required."
    
    try:
        cerbos_cli = CerbosCLI()
        
        if not cerbos_cli.check_installation():
            return "❌ Cerbos CLI not found. Install with: brew install cerbos/tap/cerbos"
        
        test_result = cerbos_cli.test(policy_yaml, test_yaml)
        
        response = "# Test Results\n\n"
        response += f"**Passed**: {test_result.passed}\n"
        response += f"**Failed**: {test_result.failed}\n"
        response += f"**Total**: {test_result.total}\n\n"
        
        if test_result.failed == 0:
            response += "✅ All tests passed!\n"
        else:
            response += "❌ Some tests failed. See details below:\n\n"
            response += f"```\n{test_result.details}\n```\n"
        
        return response
        
    except Exception as e:
        return f"Error running tests: {str(e)}"