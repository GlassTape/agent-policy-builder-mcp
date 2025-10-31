"""Validate policy tool - Cerbos CLI validation."""

from typing import Dict, Any

from .shared_utils import PolicyPipeline, format_validation_results


async def validate_policy_tool(args: Dict[str, Any]) -> str:
    """Validate policy using cerbos compile."""
    policy_yaml = args.get("policy_yaml", "")
    
    if not policy_yaml:
        return "Error: 'policy_yaml' parameter required."
    
    try:
        pipeline = PolicyPipeline()
        
        if not pipeline.cerbos_cli.check_installation():
            return "❌ Cerbos CLI not found. Install with: brew install cerbos/tap/cerbos"
        
        validation_result, _ = pipeline.validate_with_cerbos(policy_yaml)
        
        response = "# 🔍 Policy Validation\n\n"
        response += format_validation_results(validation_result)
        
        return response
        
    except Exception as e:
        return f"Error validating policy: {str(e)}"