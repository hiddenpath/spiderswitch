# ai-mcp-model-switcher list_models tool
"""
MCP tool for listing available models.
MCP工具：列出可用模型。
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)


def tool_schema() -> Tool:
    """Get the list_models tool schema."""
    return Tool(
        name="list_models",
        description=(
            "List all available models from registered providers in ai-protocol manifests. "
            "列出ai-protocol manifests中所有已注册provider的可用模型。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "filter_provider": {
                    "type": "string",
                    "description": (
                        "Optional filter by provider (e.g., 'openai', 'anthropic'). "
                        "可选，按provider过滤（如 'openai', 'anthropic'）"
                    ),
                },
                "filter_capability": {
                    "type": "string",
                    "enum": ["streaming", "tools", "vision", "embeddings", "audio"],
                    "description": (
                        "Optional filter by capability. "
                        "可选，按能力过滤"
                    ),
                },
            },
        },
    )


async def handle(runtime: Any, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle list_models tool call.

    Args:
        runtime: Runtime implementation (e.g., PythonRuntime)
        arguments: Tool arguments from MCP request

    Returns:
        List of TextContent with model list
    """
    from ..runtime.python_runtime import format_model_info

    try:
        filter_provider = arguments.get("filter_provider")
        filter_capability = arguments.get("filter_capability")

        logger.info(
            f"Listing models: filter_provider={filter_provider}, "
            f"filter_capability={filter_capability}"
        )

        # Get models from runtime
        models = await runtime.list_models(
            filter_provider=filter_provider,
            filter_capability=filter_capability,
        )

        # Format response
        result = {
            "count": len(models),
            "models": [format_model_info(m) for m in models],
        }

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return [
            TextContent(
                type="text",
                text=f'{{"status": "error", "message": "Failed to list models: {e}"}}',
            )
        ]


__all__ = ["tool_schema", "handle"]
