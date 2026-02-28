# ai-mcp-model-switcher switch_model tool
"""
MCP tool for switching AI models.
MCP工具：切换AI模型。
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import TextContent, Tool

logger = logging.getLogger(__name__)

# Tool schema definition
def tool_schema() -> Tool:
    """Get the switch_model tool schema."""
    return Tool(
        name="switch_model",
        description=(
            "Switch to a different AI model/provider. "
            "Requires provider API key configured in environment or passed explicitly. "
            "切换到不同的AI模型/provider。需要在环境变量中配置provider API密钥或显式传递。"
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": (
                        "Model identifier (e.g., 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet'). "
                        "模型标识符（如 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet'）"
                    ),
                    "pattern": "^[a-z0-9-]+/[a-z0-9-.]+$",
                },
                "api_key": {
                    "type": "string",
                    "description": (
                        "Optional explicit API key (overrides environment variable). "
                        "可选的显式API密钥（覆盖环境变量）"
                    ),
                },
                "base_url": {
                    "type": "string",
                    "description": (
                        "Optional custom base URL for testing/mock. "
                        "可选的自定义基础URL，用于测试/mock"
                    ),
                },
            },
            "required": ["model"],
        },
    )


async def handle(
    runtime: Any,
    state_manager: Any,
    arguments: dict[str, Any],
) -> list[TextContent]:
    """Handle switch_model tool call.

    Args:
        runtime: Runtime implementation (e.g., PythonRuntime)
        state_manager: State manager instance
        arguments: Tool arguments from MCP request

    Returns:
        List of TextContent with result
    """
    from ..runtime.python_runtime import (
        extract_model_from_args,
        format_model_info,
    )

    try:
        model_id, api_key, base_url = extract_model_from_args(arguments)
        logger.info(f"Switching to model: {model_id}")

        # Switch model via runtime
        model_info = await runtime.switch_model(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
        )

        # Update state
        state_manager.update_from_model_info(model_info)

        # Format response
        result = {
            "status": "success",
            "message": f"Successfully switched to {model_info.provider}/{model_info.id.split('/')[1] if '/' in model_info.id else model_info.id}",
            **format_model_info(model_info),
        }

        return [TextContent(type="text", text=str(result))]

    except ValueError as e:
        logger.error(f"Invalid argument: {e}")
        return [
            TextContent(
                type="text",
                text=f'{{"status": "error", "message": "Invalid argument: {e}"}}',
            )
        ]
    except RuntimeError as e:
        logger.error(f"Failed to switch model: {e}")
        return [
            TextContent(
                type="text",
                text=f'{{"status": "error", "message": "Failed to switch model: {e}"}}',
            )
        ]


__all__ = ["tool_schema", "handle"]
