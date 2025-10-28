"""
Optional LLM Adapter - ONLY for edge cases where client-LLM isn't available.

WARNING: Client-LLM mode is STRONGLY RECOMMENDED for:
- Air-gapped deployments
- Security compliance 
- Deterministic behavior
- Enterprise compatibility

This adapter should only be used when absolutely necessary.
"""

import os
import json
import re
from abc import ABC, abstractmethod
from typing import Optional


class LLMAdapter(ABC):
    """Abstract interface for LLM providers - use sparingly."""
    
    @abstractmethod
    def nl_to_icp(self, nl_requirements: str) -> dict:
        """Convert natural language to ICP JSON."""
        pass


class AnthropicAdapter(LLMAdapter):
    """
    Minimal Anthropic adapter - ONLY for environments without LLM-capable clients.
    
    Prefer client-LLM mode in production for security and compliance.
    """
    
    def __init__(self, api_key: str):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: "
                "pip install 'glasstape-policy-builder-mcp[anthropic]'"
            )
        self.client = Anthropic(api_key=api_key)
    
    def nl_to_icp(self, nl_requirements: str) -> dict:
        """Convert NL to ICP - prefer client-side generation."""
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fastest, cheapest model
                max_tokens=4096,
                system="""You are a policy normalizer. Output ONLY valid ICP JSON:

{
  "version": "1.0.0",
  "metadata": {"name": "snake_case", "description": "...", "resource": "..."},
  "policy": {
    "resource": "...",
    "version": "1.0.0", 
    "rules": [
      {"actions": ["..."], "effect": "EFFECT_ALLOW", "conditions": [...]},
      {"actions": ["*"], "effect": "EFFECT_DENY", "conditions": []}
    ]
  },
  "tests": [
    {"name":"positive_test","category":"positive","input":{...},"expected":"EFFECT_ALLOW"},
    {"name":"negative_test","category":"negative","input":{...},"expected":"EFFECT_DENY"}
  ]
}

Always end with default deny rule. Include at least 2 tests.""",
                messages=[{"role": "user", "content": nl_requirements}]
            )
            
            text = response.content[0].text
            json_str = self._extract_json(text)
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Failed to convert natural language to ICP: {str(e)}")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from response."""
        try:
            # Remove code blocks if present
            text = re.sub(r'```[^\n]*\n', '', text)
            text = re.sub(r'```', '', text)
            
            # Find JSON structure
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json_match.group(0)
            
            raise ValueError("No valid JSON found in LLM response")
        except Exception as e:
            raise ValueError(f"Failed to extract JSON from response: {str(e)}")


def get_llm_adapter() -> Optional[LLMAdapter]:
    """
    Get optional LLM adapter - CLIENT-LLM MODE IS PREFERRED.
    
    Returns None by default to encourage client-side generation.
    """
    provider = os.getenv('LLM_PROVIDER')
    
    if not provider:
        # This is the preferred state - no server-side LLM
        return None
    
    # Warning for discouraged usage
    print("⚠️  WARNING: Server-side LLM mode detected.")
    print("   Client-LLM mode is strongly recommended for:")
    print("   - Security compliance")
    print("   - Air-gapped deployments") 
    print("   - Deterministic behavior")
    print("   Consider removing LLM_PROVIDER env var.\n")
    
    if provider == 'anthropic':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("LLM_PROVIDER=anthropic requires ANTHROPIC_API_KEY")
        try:
            return AnthropicAdapter(api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Anthropic adapter: {str(e)}")
    
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


if __name__ == "__main__":
    adapter = get_llm_adapter()
    
    if adapter:
        print("⚠️  Server-side LLM configured (discouraged)")
    else:
        print("✓ Client-LLM mode (recommended)")