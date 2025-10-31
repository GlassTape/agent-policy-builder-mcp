"""Policy Template Library - Pre-built templates for common policy scenarios."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class PolicyTemplate:
    """Policy template definition"""
    id: str
    name: str
    category: Literal['finance', 'healthcare', 'ai_safety', 'data_access', 'system']
    description: str
    example: str


POLICY_TEMPLATES = [
    PolicyTemplate(
        id='payment_execution',
        name='Payment Execution',
        category='finance',
        description='AI agent payment policy with amount limits, sanctions screening, and rate limiting',
        example="""Allow AI agents to execute payments up to $50. Block sanctioned entities. 
Limit cumulative hourly amount to $50. Maximum 5 transactions per 5 minutes.
Topics: payment, transaction. Block topics: recipe, adult."""
    ),
    PolicyTemplate(
        id='phi_access',
        name='PHI Access',
        category='healthcare',
        description='HIPAA-compliant policy for accessing protected health information',
        example="""Allow healthcare providers to read patient records. Require role verification. 
Log all access. Block access to records of patients not under their care.
Topics: phi, medical_record, healthcare. Block topics: payment, recipe."""
    ),
    PolicyTemplate(
        id='model_invocation',
        name='AI Model Invocation Policy',
        category='ai_safety',
        description='Policy for controlling AI model invocations with prompt filtering',
        example="""Allow AI agents to invoke models for approved use cases. Block jailbreak attempts. 
Limit to 100 requests per hour. Require content filtering.
Topics: api, configuration. Block topics: adult, violence, illegal."""
    ),
    PolicyTemplate(
        id='pii_export',
        name='PII Export Control Policy',
        category='data_access',
        description='Policy for controlling export of personally identifiable information',
        example="""Allow data analysts to export anonymized data. Block export of PII fields. 
Require approval for exports over 10,000 records. Log all export operations.
Topics: pii, personal_data. Block topics: phi, medical_record."""
    ),
    PolicyTemplate(
        id='admin_access',
        name='Admin Access Policy',
        category='system',
        description='Policy for administrative system access with MFA requirements',
        example="""Allow system administrators to modify configurations. Require MFA verification. 
Block after 3 failed attempts. Require approval for production changes.
Topics: admin, configuration, security. Block topics: recipe, entertainment."""
    ),
]


class TemplateLibrary:
    """Manage policy templates"""
    
    def list_templates(self, category: str = None) -> list[PolicyTemplate]:
        """
        List available templates
        
        Args:
            category: Optional category filter
            
        Returns:
            List of matching templates
        """
        if category:
            return [t for t in POLICY_TEMPLATES if t.category == category]
        return POLICY_TEMPLATES
    
    def get_template(self, template_id: str) -> PolicyTemplate | None:
        """Get a specific template by ID"""
        for template in POLICY_TEMPLATES:
            if template.id == template_id:
                return template
        return None
    
    def get_categories(self) -> list[str]:
        """Get list of all categories"""
        return list(set(t.category for t in POLICY_TEMPLATES))
    
    def format_templates(self, templates: list[PolicyTemplate]) -> str:
        """Format templates as readable text"""
        output = "# Policy Templates\n\n"
        output += f"**Categories**: {', '.join(self.get_categories())}\n\n"
        
        for template in templates:
            output += f"## {template.name}\n"
            output += f"**ID**: `{template.id}`\n"
            output += f"**Category**: {template.category}\n"
            output += f"**Description**: {template.description}\n\n"
            output += "**Example requirement**:\n"
            output += f"```\n{template.example}\n```\n\n"
            output += "---\n\n"
        
        output += "\nUse `generate_policy` with any of these example requirements to create a policy.\n"
        
        return output

