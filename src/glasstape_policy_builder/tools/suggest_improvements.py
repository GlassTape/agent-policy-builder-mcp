"""Security analysis tool implementation."""

import json
from typing import Dict, Any

from ..redteam_analyzer import SimpleRedTeamAnalyzer


async def suggest_improvements_tool(args: Dict[str, Any]) -> str:
    """Analyze policy for security issues using 5 essential checks."""
    policy_yaml = args.get("policy_yaml", "")
    icp_json = args.get("icp_json")
    
    if not policy_yaml:
        return "Error: 'policy_yaml' parameter required."
    
    # Parse optional ICP JSON for deeper analysis
    icp = None
    if icp_json:
        try:
            icp = json.loads(icp_json) if isinstance(icp_json, str) else icp_json
        except (json.JSONDecodeError, TypeError):
            pass  # Continue without ICP data
    
    # Run security analysis
    analyzer = SimpleRedTeamAnalyzer()
    findings = analyzer.analyze(policy_yaml, icp)
    
    return analyzer.format_findings(findings)