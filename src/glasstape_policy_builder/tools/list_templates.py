"""List templates tool implementation."""

from typing import Dict, Any

from ..templates import TemplateLibrary


async def list_templates_tool(args: Dict[str, Any]) -> str:
    """List available policy templates."""
    category = args.get("category")
    
    library = TemplateLibrary()
    templates = library.list_templates(category)
    
    return library.format_templates(templates)