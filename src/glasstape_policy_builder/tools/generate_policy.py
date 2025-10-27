"""Generate policy tool implementation."""

from typing import Dict, Any

from ..types import SimpleICP
from ..icp_validator import ICPValidator
from ..cerbos_generator import CerbosGenerator
from ..cerbos_cli import CerbosCLI


async def generate_policy_tool(args: Dict[str, Any]) -> str:
    """Generate Cerbos YAML policy from ICP JSON."""
    icp_data = args.get("icp")
    
    if not icp_data:
        return "Error: 'icp' parameter required. Provide ICP JSON structure."
    
    try:
        # Validate ICP structure with Pydantic
        icp = SimpleICP.model_validate(icp_data)
        
        # Additional validation with ICPValidator
        validator = ICPValidator()
        validator.validate(icp.model_dump())
        
        # Generate Cerbos YAML using CerbosGenerator
        generator = CerbosGenerator()
        policy_yaml = generator.generate_policy(icp.model_dump())
        test_yaml = generator.generate_tests(icp.model_dump())
        
        # Validate with Cerbos CLI
        cerbos_cli = CerbosCLI()
        validation_result = None
        test_result = None
        
        if cerbos_cli.check_installation():
            # Validate policy
            validation_result = cerbos_cli.compile(policy_yaml)
            
            # Run tests if validation passed
            if validation_result.success:
                try:
                    test_result = cerbos_cli.test(policy_yaml, test_yaml)
                except Exception:
                    pass  # Test execution failure is not critical
        
        # Format response
        response = f"# Policy Generated: {icp.metadata.name}\n\n"
        response += f"{icp.metadata.description}\n\n"
        
        if icp.metadata.compliance:
            response += f"**Compliance**: {', '.join(icp.metadata.compliance)}\n\n"
        
        response += "## Cerbos Policy\n\n"
        response += f"```yaml\n{policy_yaml}\n```\n\n"
        
        response += "## Test Suite\n\n"
        response += f"```yaml\n{test_yaml}\n```\n\n"
        
        if validation_result:
            if validation_result.success:
                response += "✅ **Policy validation passed**\n\n"
            else:
                response += "❌ **Policy validation failed**\n\n"
                for error in validation_result.errors:
                    response += f"- {error}\n"
                response += "\n"
        
        if test_result:
            response += f"## Test Results: {test_result.passed}/{test_result.total} passed\n\n"
            if test_result.failed > 0:
                response += f"⚠️ {test_result.failed} tests failed\n\n"
        
        return response
        
    except Exception as e:
        return f"Error generating policy: {str(e)}"
