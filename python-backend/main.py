"""Main entry point for the OpenAI Customer Service Agents Demo (Airline).

Runs a FastAPI server that exposes a chat endpoint for the airline
customer-service multi-agent pipeline.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import Runner, trace

from airline.agents import triage_agent
from airline.context import AirlineAgentContext, AirlineAgentChatContext, create_initial_context

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Airline CS Agents Demo",
    description="Multi-agent customer-service demo powered by OpenAI Agents SDK.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> AirlineAgentChatContext
_sessions: dict[str, AirlineAgentChatContext] = {}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    # Optional: caller can supply booking/flight info to pre-populate context
    account_number: str | None = None
    confirmation_number: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_name: str | None = None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_or_create_session(
    session_id: str | None,
    account_number: str | None,
    confirmation_number: str | None,
) -> tuple[str, AirlineAgentChatContext]:
    """Return (session_id, chat_context), creating a new session when needed."""
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]

    new_id = session_id or str(uuid.uuid4())
    agent_ctx: AirlineAgentContext = create_initial_context(
        account_number=account_number,
        confirmation_number=confirmation_number,
    )
    chat_ctx = AirlineAgentChatContext(context=agent_ctx, history=[])
    _sessions[new_id] = chat_ctx
    logger.info("Created new session %s", new_id)
    return new_id, chat_ctx


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Accept a user message and return the agent's reply."""
    session_id, chat_ctx = _get_or_create_session(
        req.session_id, req.account_number, req.confirmation_number
    )

    # Append the new user turn to history
    chat_ctx.history.append({"role": "user", "content": req.message})

    try:
        with trace("airline-cs-demo", group_id=session_id):
            result = await Runner.run(
                triage_agent,
                input=chat_ctx.history,
                context=chat_ctx.context,
            )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Agent run failed for session %s", session_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    assistant_message: str = result.final_output or ""
    last_agent: Any = result.last_agent
    agent_name: str | None = getattr(last_agent, "name", None)

    # Persist the assistant turn
    chat_ctx.history.append({"role": "assistant", "content": assistant_message})

    return ChatResponse(
        session_id=session_id,
        response=assistant_message,
        agent_name=agent_name,
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    """Clear a session from the in-memory store."""
    _sessions.pop(session_id, None)
    return {"deleted": session_id}


# ---------------------------------------------------------------------------
# Dev server entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
