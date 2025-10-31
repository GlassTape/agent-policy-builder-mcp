"""Shared utilities for MCP tools to eliminate code duplication."""

from typing import Dict, Any, Optional
from ..types import SimpleICP
from ..icp_validator import ICPValidator
from ..cerbos_generator import CerbosGenerator
from ..cerbos_cli import CerbosCLI
from ..redteam_analyzer import SimpleRedTeamAnalyzer


class PolicyPipeline:
    """Shared policy processing pipeline."""
    
    def __init__(self):
        self.validator = ICPValidator()
        self.generator = CerbosGenerator()
        self.cerbos_cli = CerbosCLI()
        self.analyzer = SimpleRedTeamAnalyzer()
    
    def validate_icp(self, icp_data: Dict[str, Any]) -> SimpleICP:
        """Validate and return ICP object."""
        icp = SimpleICP.model_validate(icp_data)
        self.validator.validate(icp.model_dump())
        return icp
    
    def generate_policy_artifacts(self, icp_data: Dict[str, Any]) -> tuple[str, str]:
        """Generate policy and test YAML from ICP."""
        policy_yaml = self.generator.generate_policy(icp_data)
        test_yaml = self.generator.generate_tests(icp_data)
        return policy_yaml, test_yaml
    
    def validate_with_cerbos(self, policy_yaml: str, test_yaml: Optional[str] = None):
        """Validate policy with Cerbos CLI and optionally run tests."""
        validation_result = None
        test_result = None
        
        if self.cerbos_cli.check_installation():
            validation_result = self.cerbos_cli.compile(policy_yaml)
            
            if validation_result.success and test_yaml:
                try:
                    test_result = self.cerbos_cli.test(policy_yaml, test_yaml)
                except Exception:
                    pass  # Test failure is not critical
        
        return validation_result, test_result
    
    def analyze_security(self, policy_yaml: str, icp_data: Optional[Dict[str, Any]] = None):
        """Run security analysis on policy."""
        return self.analyzer.analyze(policy_yaml, icp_data)


def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    return text.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def format_validation_results(validation_result, test_result=None) -> str:
    """Format validation and test results consistently."""
    response = "## ✅ Validation Results\n\n"
    
    if validation_result:
        if validation_result.success:
            response += "✅ **Policy syntax valid**\n"
            if validation_result.warnings:
                response += "\n⚠️ **Warnings**:\n"
                for warning in validation_result.warnings:
                    response += f"- {warning}\n"
        else:
            response += "❌ **Policy syntax errors**:\n"
            for error in validation_result.errors:
                response += f"- {error}\n"
    else:
        response += "ℹ️ **Validation skipped** (Cerbos CLI not available)\n"
    
    response += "\n"
    
    # Test results
    if test_result:
        response += "## 🧪 Test Results\n\n"
        response += f"**Passed**: {test_result.passed}/{test_result.total}\n"
        if test_result.failed == 0:
            response += "✅ **All tests passed!**\n"
        else:
            response += f"❌ **{test_result.failed} tests failed**\n"
        response += "\n"
    
    return response


def format_policy_metadata(icp: SimpleICP) -> str:
    """Format policy metadata consistently."""
    response = ""
    
    if icp.metadata.topics:
        response += f"**Topics**: {', '.join(icp.metadata.topics)}\n"
    if icp.metadata.safety_category:
        response += f"**Safety Level**: {icp.metadata.safety_category}\n"
    if icp.metadata.compliance:
        response += f"**Compliance**: {', '.join(icp.metadata.compliance)}\n"
    
    return response + "\n" if response else ""