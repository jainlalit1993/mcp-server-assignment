"""FastAPI server: /health and /review (SSE streaming).

/review runs the main LangGraph with `astream_events` and streams one SSE message
per node start/finish, plus a final result. Node names are mapped to friendly
labels so the UI reads like a story.
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agent import config
from agent.graph import graph

app = FastAPI(title="RepoRadar", description="Multi-agent GitHub repo reviewer")

# CORS for the Vite dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Node-name -> friendly label -------------------------------------------

MAIN_LABELS = {
    "input_guardrail": "input guardrail",
    "query_reformulation": "reformulating query",
    "orchestrator": "orchestrating",
    "structure_agent": "Structure agent",
    "readme_agent": "README agent",
    "test_agent": "Test agent",
    "summarizer": "summarising",
    "answer_evaluation": "evaluating",
    "output_guardrail": "output guardrail",
    "tone_of_voice": "polishing tone",
}

INTERNAL_LABELS = {
    "execution_guardrail": "execution guard",
    "tool_selection": "selecting GitHub tools",
    "tool_execution": "calling GitHub",
    "analyze": "analysing",
}

AGENT_PREFIX = {"structure": "Structure", "readme": "README", "test": "Test"}

KNOWN_NODES = set(MAIN_LABELS) | set(INTERNAL_LABELS)


def _agent_from_ns(ns: str) -> str | None:
    """Pull the agent name out of a subgraph checkpoint namespace."""
    if not ns:
        return None
    node = ns.split("|")[0].split(":")[0]
    return node[:-6] if node.endswith("_agent") else None


def _label(name: str, ns: str) -> str:
    if name in INTERNAL_LABELS:
        prefix = AGENT_PREFIX.get(_agent_from_ns(ns) or "", "Agent")
        return f"{prefix}: {INTERNAL_LABELS[name]}"
    return MAIN_LABELS.get(name, name)


def _compact(output) -> dict | None:
    """Strip the bulky messages channel before sending node output to the UI."""
    if not isinstance(output, dict):
        return None
    trimmed = {k: v for k, v in output.items() if k != "messages"}
    return trimmed or None


# --- Routes -----------------------------------------------------------------

class ReviewRequest(BaseModel):
    repo_url: str
    question: str | None = None


@app.get("/health")
async def health():
    checks = {
        "openai_key": bool(os.environ.get("OPENAI_API_KEY")),
        "github_token": bool(os.environ.get("GITHUB_TOKEN")),
        "fast_model": config.fast_model(),
        "smart_model": config.smart_model(),
        "github_mcp": config.github_mcp_url(),
    }
    status = "ok" if checks["openai_key"] and checks["github_token"] else "degraded"
    return {"status": status, "checks": checks}


def _sse(payload: dict) -> dict:
    return {"data": json.dumps(payload)}


@app.post("/review")
async def review(req: ReviewRequest):
    initial = {"user_query": req.question or "", "repo_url": req.repo_url, "messages": []}

    async def event_generator():
        final_state: dict = {}
        seen: set = set()
        yield _sse({"type": "start", "repo_url": req.repo_url})
        try:
            async for event in graph.astream_events(initial, version="v2"):
                name = event.get("name", "")
                if name not in KNOWN_NODES:
                    continue
                kind = event["event"]
                run_id = event.get("run_id", "")
                ns = event.get("metadata", {}).get("langgraph_checkpoint_ns", "")

                if kind == "on_chain_start" and ("start", run_id) not in seen:
                    seen.add(("start", run_id))
                    yield _sse({"type": "node", "node": name, "label": _label(name, ns), "phase": "start"})

                elif kind == "on_chain_end" and ("end", run_id) not in seen:
                    seen.add(("end", run_id))
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict):
                        # Rebuild final state by merging each node's update.
                        for key, value in output.items():
                            if key in ("findings", "guardrail") and isinstance(value, dict):
                                final_state[key] = {**final_state.get(key, {}), **value}
                            elif key != "messages":
                                final_state[key] = value
                    yield _sse({
                        "type": "node", "node": name, "label": _label(name, ns),
                        "phase": "end", "data": _compact(output),
                    })

            yield _sse({"type": "final", "state": {
                "repo_url": final_state.get("repo_url", req.repo_url),
                "selected_agents": final_state.get("selected_agents", []),
                "findings": final_state.get("findings", {}),
                "summary": final_state.get("summary", ""),
                "evaluation": final_state.get("evaluation", {}),
                "final_answer": final_state.get("final_answer", ""),
                "guardrail": final_state.get("guardrail", {}),
            }})
        except Exception as exc:  # surface failures to the UI instead of a dead stream
            yield _sse({"type": "error", "message": str(exc)})
        yield _sse({"type": "done"})

    return EventSourceResponse(event_generator())


# Serve the built frontend at "/" in production (if it has been built).
_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
