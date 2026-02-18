"""
FastAPI server for cryptocurrency trading AI agent.
"""
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.crypto_agent import create_crypto_agent
from db.mongo import init_wallet, get_wallet, get_transactions, get_mcp_logs, clear_mcp_logs

load_dotenv()

# Agent cache per user (optional optimization)
_agent_cache: dict = {}


def get_agent(user_id: str):
    """Get or create agent for user."""
    if user_id not in _agent_cache:
        _agent_cache[user_id] = create_crypto_agent(user_id)
    return _agent_cache[user_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init default wallet."""
    init_wallet("user_default")
    yield
    # Shutdown: cleanup if needed


app = FastAPI(title="Crypto Trading AI Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        *([os.getenv("FRONTEND_URL")] if os.getenv("FRONTEND_URL") else []),
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Mount FastMCP SSE endpoint for external MCP clients ───────────

try:
    from mcp_server.server import mcp as fastmcp_server
    app.mount("/mcp", fastmcp_server.sse_app())
except Exception:
    pass  # FastMCP SSE mount is optional; don't break if unavailable


# ── Request / Response models ────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    user_id: str = "user_default"


class AgentStep(BaseModel):
    thought: str = ""
    tool: str = ""
    tool_input: Dict[str, Any] = {}
    tool_output: str = ""
    mcp_request: Dict[str, Any] = {}
    mcp_response: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    response: str
    user_id: str
    steps: List[AgentStep] = []


# ── Helper: extract steps from agent result + MCP log ────────────

def _build_steps(result: dict, mcp_server) -> List[AgentStep]:
    """Combine LangChain intermediate steps with MCP log entries."""
    intermediate = result.get("intermediate_steps", [])
    mcp_log = mcp_server.get_log() if mcp_server else []

    steps: List[AgentStep] = []
    mcp_idx = 0

    for action, observation in intermediate:
        tool_name = getattr(action, "tool", "")
        tool_input = getattr(action, "tool_input", {})
        if isinstance(tool_input, str):
            tool_input = {"input": tool_input}
        thought = getattr(action, "log", "")

        # Find the matching MCP log entry
        mcp_req: Dict[str, Any] = {}
        mcp_resp: Dict[str, Any] = {}
        while mcp_idx < len(mcp_log):
            entry = mcp_log[mcp_idx]
            mcp_idx += 1
            if entry.get("type") == "tools/call":
                mcp_req = entry.get("request", {})
                mcp_resp = entry.get("response", {})
                break

        steps.append(AgentStep(
            thought=thought,
            tool=tool_name,
            tool_input=tool_input,
            tool_output=str(observation) if observation else "",
            mcp_request=mcp_req,
            mcp_response=mcp_resp,
        ))

    return steps


# ── Endpoints ────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main agent endpoint: process user message and return agent response."""
    try:
        agent = get_agent(request.user_id)
        mcp_server = getattr(agent, "mcp_server", None)

        # Clear MCP log before each request so steps align
        if mcp_server:
            mcp_server.clear_log()

        result = agent.invoke({"input": request.message})
        output = result.get("output", "Sorry, I could not process your request.")
        steps = _build_steps(result, mcp_server)

        return ChatResponse(response=output, user_id=request.user_id, steps=steps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp-log/{user_id}")
def mcp_log(user_id: str, source: str = "live", limit: int = 50, skip: int = 0):
    """
    Return MCP request/response log.
    source=live  -> current session (in-memory)
    source=history -> all past logs from MongoDB (paginated)
    """
    if source == "history":
        logs = get_mcp_logs(user_id, limit=limit, skip=skip)
        return {"mcp_calls": logs}

    # Default: live (in-memory)
    agent = _agent_cache.get(user_id)
    if not agent:
        return {"mcp_calls": []}
    mcp_server = getattr(agent, "mcp_server", None)
    if not mcp_server:
        return {"mcp_calls": []}
    return {"mcp_calls": mcp_server.get_log()}


@app.delete("/mcp-log/{user_id}")
def delete_mcp_log(user_id: str):
    """Clear all persisted MCP logs for a user."""
    count = clear_mcp_logs(user_id)
    return {"deleted": count}


@app.get("/balance/{user_id}")
def balance(user_id: str):
    """Get wallet balance (no LLM call)."""
    try:
        init_wallet(user_id)
        wallet = get_wallet(user_id)
        return {"user_id": user_id, "assets": wallet}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions/{user_id}")
def transactions(user_id: str, limit: int = 20):
    """Get recent transactions (no LLM call)."""
    try:
        txs = get_transactions(user_id, limit)
        serializable = []
        for t in txs:
            t_copy = dict(t)
            t_copy["_id"] = str(t["_id"])
            serializable.append(t_copy)
        return {"user_id": user_id, "transactions": serializable}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") != "production",
    )
