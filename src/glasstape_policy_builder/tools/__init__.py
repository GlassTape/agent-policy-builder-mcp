"""MCP tools for policy generation and analysis."""

from mcp.server import Server
from mcp import types
from typing import Dict, Any, List, Optional

from .generate_policy import generate_policy_tool
from .validate_policy import validate_policy_tool
from .suggest_improvements import suggest_improvements_tool
from .list_templates import list_templates_tool


async def register_tools(server: Server):
    """Register consolidated MCP tools with the server."""
    
    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available MCP tools."""
        return [
            types.Tool(
                name="generate_policy",
                description="Convert natural language guardrails into enterprise-grade Cerbos YAML policies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nl_requirements": {
                            "type": "string",
                            "description": "Plain English description of AI guardrail or security policy"
                        },
                        "icp": {
                            "type": "object",
                            "description": "Structured policy JSON (for automation workflows)"
                        }
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
                name="suggest_improvements",
                description="Analyze policy for security issues and suggest improvements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_yaml": {"type": "string"},
                        "icp": {"type": "object", "description": "Optional ICP for enhanced analysis"}
                    },
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
            elif name == "suggest_improvements":
                result = await suggest_improvements_tool(arguments)
            elif name == "list_templates":
                result = await list_templates_tool(arguments)
            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]