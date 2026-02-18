"""
MCP Bridge — connects LangChain tools to MCP server handlers with JSON-RPC logging.

Replaces the old MCPSimulator. Calls handlers directly (in-process) while
constructing JSON-RPC 2.0 request/response log entries for the MCP Inspector UI.
Tool definitions are sourced from server.py (the FastMCP single source of truth).
"""
import time
from functools import partial
from typing import Any, Callable, Dict, List, Optional

from mcp_server.utils import format_for_display


class MCPBridge:
    """
    Bridge between LangChain agent tools and MCP server handlers.

    - Calls handler functions directly (no transport overhead)
    - Formats every call as a JSON-RPC 2.0 request/response pair
    - Logs interactions for the MCP Inspector UI
    - Persists logs to MongoDB via callback
    """

    def __init__(
        self,
        user_id: str,
        persist_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self._user_id = user_id
        self._call_log: List[Dict[str, Any]] = []
        self._next_id: int = 1
        self._persist = persist_callback
        self._tools = self._build_tool_registry(user_id)

    def _build_tool_registry(self, user_id: str) -> Dict[str, dict]:
        """
        Build tool registry from TOOL_SPECS + handlers.
        User-bound handlers get user_id injected via functools.partial.
        """
        from mcp_server.server import TOOL_SPECS
        from mcp_server.handlers import (
            handle_get_price,
            handle_get_orderbook,
            handle_buy_crypto,
            handle_check_balance,
            handle_transaction_history,
        )

        handler_map: Dict[str, Callable] = {
            "get_crypto_price": handle_get_price,
            "get_orderbook": handle_get_orderbook,
            "buy_crypto": partial(handle_buy_crypto, user_id),
            "check_balance": partial(handle_check_balance, user_id),
            "transaction_history": partial(handle_transaction_history, user_id),
        }

        registry: Dict[str, dict] = {}
        for spec in TOOL_SPECS:
            name = spec["name"]
            registry[name] = {
                "name": name,
                "description": spec["description"],
                "inputSchema": spec["inputSchema"],
                "handler": handler_map[name],
            }
        return registry

    # ── tools/list ────────────────────────────────────────────────

    def list_tools(self) -> dict:
        """Return a JSON-RPC 2.0 tools/list response and log it."""
        req_id = self._next_id
        self._next_id += 1

        request: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": req_id,
        }

        tools_list = [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"],
            }
            for t in self._tools.values()
        ]

        response: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": req_id,
        }

        entry = {
            "type": "tools/list",
            "request": request,
            "response": response,
            "timestamp": time.time(),
        }
        self._call_log.append(entry)
        if self._persist:
            self._persist(entry)
        return response

    # ── tools/call ────────────────────────────────────────────────

    def call_tool(self, name: str, arguments: dict) -> dict:
        """
        Call a tool handler and log the JSON-RPC 2.0 request/response pair.

        The handler returns a structured Dict (success/data/error).
        The bridge converts it to a JSON-RPC response with text content
        for LLM consumption, and stores the raw structured result
        in the log for the Inspector.
        """
        req_id = self._next_id
        self._next_id += 1

        request: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
            "id": req_id,
        }

        tool = self._tools.get(name)
        if tool is None:
            response: Dict[str, Any] = {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool not found: {name}"},
                "id": req_id,
            }
        else:
            try:
                result = tool["handler"](**arguments)
                result_text = format_for_display(result)
                is_error = not result.get("success", False)
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [{"type": "text", "text": result_text}],
                        "isError": is_error,
                        "_structured": result,
                    },
                    "id": req_id,
                }
            except Exception as exc:
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {exc}"}],
                        "isError": True,
                    },
                    "id": req_id,
                }

        entry = {
            "type": "tools/call",
            "request": request,
            "response": response,
            "timestamp": time.time(),
        }
        self._call_log.append(entry)
        if self._persist:
            self._persist(entry)
        return response

    # ── Log access (for the UI) ───────────────────────────────────

    def get_log(self) -> List[Dict[str, Any]]:
        """Return the full call log."""
        return list(self._call_log)

    def clear_log(self) -> None:
        """Reset the call log and request ID counter."""
        self._call_log.clear()
        self._next_id = 1
