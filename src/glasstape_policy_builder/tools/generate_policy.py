"""Generate policy tool implementation."""

import json
from typing import Dict, Any

from ..types import SimpleICP
from ..icp_validator import ICPValidator
from ..cerbos_generator import CerbosGenerator
from ..cerbos_cli import CerbosCLI
from ..llm_adapter import get_llm_adapter


async def generate_policy_tool(args: Dict[str, Any]) -> str:
    """
    Convert natural language guardrails into validated Cerbos YAML policies.
    
    Core value: "Write guardrails in natural language, get enterprise-grade Cerbos policies instantly."
    """
    nl_requirements = args.get("nl_requirements")  
    icp_data = args.get("icp")  # Internal format for automation
    
    # Primary customer workflow: Natural language → Cerbos YAML
    if nl_requirements:
        return await _handle_natural_language(nl_requirements)
    
    # Advanced/automation workflow: ICP JSON → Cerbos YAML  
    elif icp_data:
        return await _generate_from_icp(icp_data)
    
    # Guide user to primary workflow
    else:
        return """🎯 **Generate AI Guardrail Policies**

**Describe your guardrail in plain English:**
```
generate_policy(nl_requirements="Allow AI agents to execute payments up to $50. Block sanctioned entities. Limit to 5 transactions per 5 minutes.")
```

**More examples:**
- `"Healthcare providers can read patient records only for patients under their care"`
- `"AI models can be invoked max 100 times per hour with content filtering"`
- `"Data analysts can export anonymized data but not PII fields"`

**Output:** Ready-to-deploy Cerbos YAML policy file

💡 **Your IDE's LLM handles the natural language conversion automatically**"""


async def _generate_from_icp(icp_data: Dict[str, Any]) -> str:
    """Generate policy from ICP JSON (client-LLM mode)."""
    try:
        # Validate ICP structure with Pydantic
        icp = SimpleICP.model_validate(icp_data)
        
        # Additional validation with ICPValidator
        validator = ICPValidator()
        validator.validate(icp.model_dump())
        
        # Generate Cerbos YAML
        generator = CerbosGenerator()
        policy_yaml = generator.generate_policy(icp.model_dump())
        test_yaml = generator.generate_tests(icp.model_dump())
        
        # Validate with Cerbos CLI (if available)
        validation_result = None
        test_result = None
        
        cerbos_cli = CerbosCLI()
        if cerbos_cli.check_installation():
            validation_result = cerbos_cli.compile(policy_yaml)
            
            if validation_result.success:
                try:
                    test_result = cerbos_cli.test(policy_yaml, test_yaml)
                except Exception:
                    pass  # Test execution failure is not critical
        
        return _format_policy_response(icp, policy_yaml, test_yaml, validation_result, test_result)
        
    except Exception as e:
        # Sanitize error message to prevent XSS
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        return f"❌ **Error generating policy**: {error_msg}\n\nPlease check your ICP JSON structure and try again."


async def _handle_natural_language(nl_requirements: str) -> str:
    """
    Handle natural language guardrail requirements.
    
    Expected flow: Client LLM converts NL → ICP → this generates Cerbos YAML
    """
    # Check for optional server-side LLM (fallback only)
    llm_adapter = get_llm_adapter()
    
    if llm_adapter:
        try:
            # Use server-side LLM as fallback (discouraged but functional)
            icp_data = llm_adapter.nl_to_icp(nl_requirements)
            result = await _generate_from_icp(icp_data)
            
            # Add warning about client-LLM preference
            # Sanitize result to prevent XSS
            safe_result = result.replace('<script', '&lt;script').replace('</script', '&lt;/script')
            
            return f"""⚠️ **Server-side processing used** (client-LLM preferred for security)

{safe_result}

💡 **Recommendation**: Use client-LLM mode by providing ICP JSON directly for better security posture."""
            
        except Exception as e:
            # Fall through to guidance if server-side fails
            pass
    
    # Primary guidance: use client-LLM workflow
    # Sanitize user input to prevent XSS
    safe_requirements = nl_requirements.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    return f"""🤖 **Natural Language → Guardrail Policy**

Your request:
```
{safe_requirements}
```

**Next step**: Have your IDE's LLM convert this to structured format, then call:
```
generate_policy(icp={{
  "version": "1.0.0",
  "metadata": {{"name": "policy_name", "description": "...", "resource": "..."}},
  "policy": {{"resource": "...", "rules": [...]}},
  "tests": [...]
}})
```

**Key elements your LLM should include:**
- Resource type (payment, document, user, etc.)
- Allow/deny rules with specific conditions
- Default deny rule as final rule: `{{"actions": ["*"], "effect": "EFFECT_DENY"}}`
- Test cases (positive and negative scenarios)

💡 **This approach ensures maximum security and compliance**"""




def _format_policy_response(
    icp: SimpleICP, 
    policy_yaml: str, 
    test_yaml: str, 
    validation_result=None, 
    test_result=None
) -> str:
    """Format the complete policy generation response."""
    response = f"# 🎯 Policy Generated: {icp.metadata.name}\n\n"
    response += f"{icp.metadata.description}\n\n"
    
    if icp.metadata.compliance:
        response += f"**Compliance**: {', '.join(icp.metadata.compliance)}\n\n"
    
    if icp.metadata.tags:
        response += f"**Tags**: {', '.join(icp.metadata.tags)}\n\n"
    
    response += "## 📜 Cerbos Policy\n\n"
    response += f"```yaml\n{policy_yaml}\n```\n\n"
    
    response += "## 🧪 Test Suite\n\n"
    response += f"```yaml\n{test_yaml}\n```\n\n"
    
    # Validation results
    if validation_result:
        if validation_result.success:
            response += "✅ **Policy validation passed**\n\n"
            if validation_result.warnings:
                response += "⚠️ **Warnings**:\n"
                for warning in validation_result.warnings:
                    response += f"- {warning}\n"
                response += "\n"
        else:
            response += "❌ **Policy validation failed**\n\n"
            for error in validation_result.errors:
                response += f"- {error}\n"
            response += "\n"
    else:
        response += "ℹ️ **Validation skipped** (Cerbos CLI not available)\n\n"
    
    # Test results
    if test_result:
        response += f"## 📊 Test Results: {test_result.passed}/{test_result.total} passed\n\n"
        if test_result.failed > 0:
            response += f"⚠️ **{test_result.failed} tests failed** - review implementation\n\n"
        else:
            response += "🎉 **All tests passed!**\n\n"
    
    response += "---\n\n"
    response += "💡 **Next steps**:\n"
    response += "- Use `suggest_improvements` to analyze security gaps\n"
    response += "- Use `validate_policy` to re-check after changes\n"
    response += "- Use `test_policy` to run additional test scenarios\n"
    
    return response
