"""Security analysis tool implementation."""

from typing import Dict, Any


async def suggest_improvements_tool(args: Dict[str, Any]) -> str:
    """Suggest policy improvements and analyze for security issues."""
    policy_yaml = args.get("policy_yaml", "")
    
    if not policy_yaml:
        return "Error: 'policy_yaml' parameter required."
    
    findings = []
    
    # Check 1: Default deny rule
    if "EFFECT_DENY" in policy_yaml and 'actions: ["*"]' in policy_yaml:
        findings.append("✅ Default deny rule present")
    else:
        findings.append("❌ Missing default deny rule")
    
    # Check 2: Overly permissive rules
    if 'actions: ["*"]' in policy_yaml and "EFFECT_ALLOW" in policy_yaml:
        findings.append("❌ Overly permissive allow rule detected")
    else:
        findings.append("✅ No overly permissive rules")
    
    # Check 3: Conditional access
    if "condition:" in policy_yaml:
        findings.append("✅ Conditional access controls present")
    else:
        findings.append("⚠️ No conditional access controls")
    
    # Check 4: Role-based access
    if "roles:" in policy_yaml:
        findings.append("✅ Role-based access control implemented")
    else:
        findings.append("⚠️ No role-based access control")
    
    passed = sum(1 for f in findings if f.startswith("✅"))
    total = len(findings)
    
    response = f"## Security Analysis\n\n**Score**: {passed}/{total} checks passed\n\n"
    
    for finding in findings:
        response += f"{finding}\n"
    
    return response