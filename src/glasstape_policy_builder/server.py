#!/usr/bin/env python3
"""MCP server for GlassTape Agent Policy Builder."""

import asyncio
from mcp import Server
from mcp.server.stdio import stdio_server

from .tools import register_tools


async def main():
    """Run the MCP server."""
    server = Server("glasstape-policy-builder")
    
    # Register all tools
    await register_tools(server)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())