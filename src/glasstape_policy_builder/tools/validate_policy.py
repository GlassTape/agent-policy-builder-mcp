"""Validate policy tool implementation."""

from typing import Dict, Any

from ..cerbos_cli import CerbosCLI


async def validate_policy_tool(args: Dict[str, Any]) -> str:
    """Validate policy using cerbos compile."""
    policy_yaml = args.get("policy_yaml", "")
    
    if not policy_yaml:
        return "Error: 'policy_yaml' parameter required."
    
    try:
        cerbos_cli = CerbosCLI()
        
        if not cerbos_cli.check_installation():
            return "❌ Cerbos CLI not found. Install with: brew install cerbos/tap/cerbos"
        
        validation_result = cerbos_cli.compile(policy_yaml)
        
        if validation_result.success:
            response = "✅ Policy validation passed!\n\n"
            if validation_result.warnings:
                response += "## Warnings\n\n"
                for warning in validation_result.warnings:
                    response += f"- {warning}\n"
            return response
        else:
            response = "❌ Policy validation failed\n\n"
            response += "## Errors\n\n"
            for error in validation_result.errors:
                response += f"- {error}\n"
            return response
            
    except Exception as e:
        return f"Error validating policy: {str(e)}"
