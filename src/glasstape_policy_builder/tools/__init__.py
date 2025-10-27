"""MCP tools for policy generation and analysis."""

from mcp import Server, types
from typing import Dict, Any, List, Optional

from .generate_policy import generate_policy_tool
from .validate_policy import validate_policy_tool
from .test_policy import test_policy_tool
from .suggest_improvements import suggest_improvements_tool
from .list_templates import list_templates_tool


async def register_tools(server: Server):
    """Register all MCP tools with the server."""
    
    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available MCP tools."""
        return [
            types.Tool(
                name="generate_policy",
                description="Generate Cerbos YAML policy from ICP JSON or natural language",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "icp": {"type": "object", "description": "ICP JSON structure (preferred)"},
                        "nl_requirements": {"type": "string", "description": "Natural language requirements"}
                    }
                }
            ),
            types.Tool(
                name="validate_policy",
                description="Validate policy syntax using cerbos compile",
                inputSchema={
                    "type": "object",
                    "properties": {"policy_yaml": {"type": "string"}},
                    "required": ["policy_yaml"]
                }
            ),
            types.Tool(
                name="test_policy",
                description="Run test suite against policy using cerbos test",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_yaml": {"type": "string"},
                        "test_yaml": {"type": "string"}
                    },
                    "required": ["policy_yaml", "test_yaml"]
                }
            ),
            types.Tool(
                name="suggest_improvements",
                description="Analyze policy for security issues and suggest improvements",
                inputSchema={
                    "type": "object",
                    "properties": {"policy_yaml": {"type": "string"}},
                    "required": ["policy_yaml"]
                }
            ),
            types.Tool(
                name="list_templates",
                description="List available policy templates",
                inputSchema={
                    "type": "object",
                    "properties": {"category": {"type": "string"}}
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Optional[Dict[str, Any]]
    ) -> List[types.TextContent]:
        """Handle MCP tool calls."""
        try:
            if not arguments:
                arguments = {}
            
            if name == "generate_policy":
                result = await generate_policy_tool(arguments)
            elif name == "validate_policy":
                result = await validate_policy_tool(arguments)
            elif name == "test_policy":
                result = await test_policy_tool(arguments)
            elif name == "suggest_improvements":
                result = await suggest_improvements_tool(arguments)
            elif name == "list_templates":
                result = await list_templates_tool(arguments)
            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]