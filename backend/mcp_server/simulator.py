"""
In-process MCP server simulator.
Speaks the MCP JSON-RPC 2.0 format but runs everything in-memory.
Logs every request/response for UI display.
"""
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class MCPTool:
    """A single registered tool in the MCP server."""

    name: str
    description: str
    input_schema: dict
    handler: Callable[..., str]


class MCPSimulator:
    """
    Simulated MCP server that formats calls as JSON-RPC 2.0
    and logs every request/response pair for the frontend to display.
    """

    def __init__(self, persist_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self._tools: Dict[str, MCPTool] = {}
        self._call_log: List[Dict[str, Any]] = []
        self._next_id: int = 1
        self._persist = persist_callback

    # ── Tool registration ────────────────────────────────────────

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict,
        handler: Callable[..., str],
    ) -> None:
        """Register a tool handler (equivalent to an MCP server declaring tools)."""
        self._tools[name] = MCPTool(name, description, input_schema, handler)

    # ── tools/list ───────────────────────────────────────────────

    def list_tools(self) -> dict:
        """Simulate the MCP ``tools/list`` response."""
        req_id = self._next_id
        self._next_id += 1

        request: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": req_id,
        }

        tools_list = [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.input_schema,
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

    # ── tools/call ───────────────────────────────────────────────

    def call_tool(self, name: str, arguments: dict) -> dict:
        """
        Simulate the MCP ``tools/call`` request → response cycle.
        Builds JSON-RPC request, calls the handler, wraps the result,
        and logs everything.
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
                result_text = tool.handler(**arguments)
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [{"type": "text", "text": result_text}],
                        "isError": False,
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

    # ── Log access (for the UI) ──────────────────────────────────

    def get_log(self) -> List[Dict[str, Any]]:
        """Return the full call log."""
        return list(self._call_log)

    def clear_log(self) -> None:
        """Reset the call log."""
        self._call_log.clear()
        self._next_id = 1
