#!/usr/bin/env python3
"""
GlassTape Agent Policy Builder MCP Server

Transforms natural language into Cerbos policies via MCP protocol.
Designed for client-LLM mode with optional server-side parsing.
"""

import asyncio
import logging
import sys
from pathlib import Path

from mcp import Server
from mcp.server.stdio import stdio_server

from .tools import register_tools
from .cerbos_cli import CerbosCLI
from .llm_adapter import get_llm_adapter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


async def main():
    """
    Run the MCP server with proper initialization and error handling.
    
    Follows MCP best practices:
    - Clear server identification
    - Graceful error handling  
    - Environment validation
    - Tool registration
    """
    try:
        # Create server with clear name
        server = Server("glasstape-policy-builder")
        logger.info("🚀 Starting GlassTape Policy Builder MCP Server")
        
        # Validate environment and dependencies
        try:
            await validate_environment()
        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            raise
        
        # Register all MCP tools
        try:
            await register_tools(server)
            logger.info("✅ All MCP tools registered successfully")
        except Exception as e:
            logger.error(f"❌ Tool registration failed: {e}")
            raise
        
        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🔗 MCP server listening on stdio")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"💥 Server failed to start: {e}")
        logger.error("Check logs above for specific error details")
        sys.exit(1)


async def validate_environment():
    """
    Validate environment and log configuration status.
    
    Follows design principle: fail fast with clear error messages.
    """
    # Check Cerbos CLI availability
    cerbos_cli = CerbosCLI()
    if cerbos_cli.check_installation():
        logger.info("✅ Cerbos CLI detected and ready")
    else:
        logger.warning("⚠️  Cerbos CLI not found - validation/testing disabled")
        logger.warning("   Install: brew install cerbos/tap/cerbos")
    
    # Check LLM adapter configuration (optional)
    llm_adapter = get_llm_adapter()
    if llm_adapter:
        logger.info("🤖 Server-side LLM adapter configured")
        logger.warning("   ⚠️  Client-LLM mode is recommended for security")
    else:
        logger.info("🎯 Client-LLM mode active (recommended)")
    
    # Check working directory permissions
    try:
        work_dir = Path("/tmp/glasstape-policies")
        work_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Work directory ready: {work_dir}")
    except PermissionError:
        logger.error("❌ Cannot create work directory - check permissions")
        raise


if __name__ == "__main__":
    asyncio.run(main())