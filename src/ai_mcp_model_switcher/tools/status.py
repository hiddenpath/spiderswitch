# ai-mcp-model-switcher get_status tool
"""
MCP tool for getting current model status.
MCP工具：获取当前模型状态。
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)


def tool_schema() -> Tool:
    """Get the get_status tool schema."""
    return Tool(
        name="get_status",
        description=(
            "Get current model status and configuration. "
            "获取当前模型状态和配置。"
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    )


async def handle(state_manager: Any) -> list[TextContent]:
    """Handle get_status tool call.

    Args:
        state_manager: State manager instance

    Returns:
        List of TextContent with status
    """
    try:
        state = state_manager.get_state()

        result = state.to_dict()

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return [
            TextContent(
                type="text",
                text=f'{{"status": "error", "message": "Failed to get status: {e}"}}',
            )
        ]


__all__ = ["tool_schema", "handle"]
