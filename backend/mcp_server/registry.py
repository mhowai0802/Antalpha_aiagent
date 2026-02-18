"""
Factory that creates an MCPBridge for a given user.
Tool definitions come from server.py (the FastMCP single source of truth).
"""
from functools import partial

from mcp_server.bridge import MCPBridge
from db.mongo import insert_mcp_log


def create_mcp_server(user_id: str) -> MCPBridge:
    """Create an MCP bridge instance bound to a specific user."""
    persist = partial(insert_mcp_log, user_id)
    return MCPBridge(user_id=user_id, persist_callback=persist)
