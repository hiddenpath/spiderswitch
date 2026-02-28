from __future__ import annotations

# ai-mcp-model-switcher
"""
Model Context Protocol server for dynamic AI model switching in ai-lib ecosystem.
MCP服务器，用于ai-lib生态系统中的动态AI模型切换。
"""

# Lazy import to avoid loading mcp dependency on package import
# This allows the package to be imported in tests without mcp installed

def main() -> None:
    """Main entry point for the MCP server."""
    from ai_mcp_model_switcher.server import cli

    cli()


__all__ = ["main"]

__version__ = "0.1.0"
