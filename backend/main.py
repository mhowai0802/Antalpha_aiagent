"""
FastAPI server for cryptocurrency trading AI agent.
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.crypto_agent import create_crypto_agent
from db.mongo import init_wallet, get_wallet, get_transactions

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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    user_id: str = "user_default"


class ChatResponse(BaseModel):
    response: str
    user_id: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main agent endpoint: process user message and return agent response."""
    try:
        agent = get_agent(request.user_id)
        result = agent.invoke({"input": request.message})
        output = result.get("output", "Sorry, I could not process your request.")
        return ChatResponse(response=output, user_id=request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Convert ObjectId to str for JSON serialization
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
        reload=True,
    )
