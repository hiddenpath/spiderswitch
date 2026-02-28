# ai-mcp-model-switcher MCP server
"""
MCP server entry point for model switching.
MCP服务器主入口，提供模型切换功能。
"""

from __future__ import annotations

import asyncio
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .runtime import PythonRuntime
from .state import ModelStateManager
from .tools import list, status, switch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# MCP server instance
app = Server("ai-mcp-model-switcher")

# Runtime instance (Python implementation using ai-lib-python)
runtime = PythonRuntime()

# State manager
state_manager = ModelStateManager()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Expose available MCP tools.

    Returns:
        List of Tool objects
    """
    return [
        switch.tool_schema(),
        list.tool_schema(),
        status.tool_schema(),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Handle tool calls.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of response content
    """
    try:
        if name == "switch_model":
            return await switch.handle(runtime, state_manager, arguments)
        elif name == "list_models":
            return await list.handle(runtime, arguments)
        elif name == "get_status":
            return await status.handle(state_manager)
        else:
            return [
                {
                    "type": "text",
                    "text": f'{{"status": "error", "message": "Unknown tool: {name}"}}',
                }
            ]
    except Exception as e:
        logger.exception(f"Error handling tool call '{name}': {e}")
        return [
            {
                "type": "text",
                "text": f'{{"status": "error", "message": "Internal error: {e}"}}',
            }
        ]


async def main() -> None:
    """Main entry point for the MCP server.

    Runs the stdio server and handles cleanup on shutdown.
    """
    logger.info("Starting ai-mcp-model-switcher MCP server")

    try:
        # Run stdio server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        try:
            await runtime.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        logger.info("Server shutdown complete")


def cli() -> None:
    """CLI entry point for the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()


__all__ = ["main", "cli"]
