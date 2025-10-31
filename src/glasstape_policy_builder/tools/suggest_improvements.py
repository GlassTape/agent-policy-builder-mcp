"""Security analysis tool - red team analysis and improvements."""

from typing import Dict, Any, Optional

from .shared_utils import PolicyPipeline


async def suggest_improvements_tool(args: Dict[str, Any]) -> str:
    """Analyze policy for security issues using 6 essential checks."""
    policy_yaml = args.get("policy_yaml", "")
    icp_data = args.get("icp")
    
    if not policy_yaml:
        return "Error: 'policy_yaml' parameter required."
    
    try:
        pipeline = PolicyPipeline()
        findings = pipeline.analyze_security(policy_yaml, icp_data)
        
        response = "# 🔒 Security Analysis\n\n"
        response += pipeline.analyzer.format_findings(findings)
        
        return response
        
    except Exception as e:
        return f"Error analyzing policy: {str(e)}"