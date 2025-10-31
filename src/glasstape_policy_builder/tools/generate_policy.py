"""Generate policy tool - primary policy generation workflow."""

from typing import Dict, Any

from .shared_utils import PolicyPipeline, sanitize_user_input, format_validation_results, format_policy_metadata
from ..llm_adapter import get_llm_adapter
from ..topic_taxonomy import taxonomy


async def generate_policy_tool(args: Dict[str, Any]) -> str:
    """
    Convert natural language guardrails into validated Cerbos YAML policies.
    
    Primary workflow: Natural language → ICP → Cerbos YAML
    """
    nl_requirements = args.get("nl_requirements")  
    icp_data = args.get("icp")
    
    # Primary workflow: Natural language → Cerbos YAML
    if nl_requirements:
        return await _handle_natural_language(nl_requirements)
    
    # Advanced workflow: ICP JSON → Cerbos YAML  
    elif icp_data:
        return await _generate_from_icp(icp_data)
    
    # Usage guidance
    else:
        return _get_usage_guidance()


async def _handle_natural_language(nl_requirements: str) -> str:
    """Handle natural language guardrail requirements."""
    llm_adapter = get_llm_adapter()
    
    if llm_adapter:
        try:
            # Server-side LLM fallback
            icp_data = llm_adapter.nl_to_icp(nl_requirements)
            result = await _generate_from_icp(icp_data)
            
            return f"""⚠️ **Server-side processing used** (client-LLM preferred)

{result}

💡 **Recommendation**: Use client-LLM mode for better security posture."""
            
        except Exception:
            pass
    
    # Primary guidance: client-LLM workflow
    safe_requirements = sanitize_user_input(nl_requirements)
    
    return f"""🤖 **Enhanced Policy Generation**

Your request:
```
{safe_requirements}
```

**Next step**: Have your IDE's LLM convert this to structured format:

```
generate_policy(icp={{
  "version": "1.0.0",
  "metadata": {{
    "name": "policy_name",
    "description": "...",
    "resource": "...",
    "topics": ["payment", "pii"],
    "blocked_topics": ["adult"],
    "safety_category": "PG_13"
  }},
  "policy": {{"resource": "...", "rules": [...]}},
  "tests": [...]
}})
```

{taxonomy.get_topic_guidance()}"""


async def _generate_from_icp(icp_data: Dict[str, Any]) -> str:
    """Generate policy from ICP JSON."""
    try:
        pipeline = PolicyPipeline()
        
        # Validate ICP and generate policy
        icp = pipeline.validate_icp(icp_data)
        policy_yaml, test_yaml = pipeline.generate_policy_artifacts(icp.model_dump())
        
        # Validate with Cerbos CLI
        validation_result, test_result = pipeline.validate_with_cerbos(policy_yaml, test_yaml)
        
        # Format response
        response = f"# 🎯 Policy Generated: {icp.metadata.name}\n\n"
        response += f"{icp.metadata.description}\n\n"
        response += format_policy_metadata(icp)
        
        response += "## 📜 Cerbos Policy\n\n"
        response += f"```yaml\n{policy_yaml}\n```\n\n"
        
        response += "## 🧪 Test Suite\n\n"
        response += f"```yaml\n{test_yaml}\n```\n\n"
        
        response += format_validation_results(validation_result, test_result)
        
        response += "💡 **Next steps**:\n"
        response += "- Use `suggest_improvements` to analyze security gaps\n"
        response += "- Use `validate_policy` to re-check after changes\n"
        
        return response
        
    except Exception as e:
        error_msg = sanitize_user_input(str(e))
        return f"❌ **Error generating policy**: {error_msg}"


def _get_usage_guidance() -> str:
    """Return usage guidance."""
    return """# 🎯 Generate Policy

## Primary Workflow

### Natural Language → Policy
```
generate_policy(nl_requirements="Allow payments up to $50. Block sanctioned entities.")
```

### ICP JSON → Policy  
```
generate_policy(icp={
  "version": "1.0.0",
  "metadata": {"name": "...", "topics": ["payment"]},
  "policy": {"resource": "...", "rules": [...]},
  "tests": [...]
})
```

## Output Includes:
✅ **Cerbos YAML Policy**: Production-ready policy file
✅ **Test Suite**: Comprehensive test cases
✅ **Validation**: Syntax checking with Cerbos CLI
✅ **Topic Governance**: Content safety and categorization

💡 **Primary tool for policy generation**"""