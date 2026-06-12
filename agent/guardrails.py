"""Three guardrails, all on the FAST model.

- input_guardrail   : runs first in the MAIN graph. Valid repo URL? on-topic? safe?
- execution_guardrail: runs first in EACH agent subgraph, before any tool use.
- output_guardrail   : runs before finalising. Grounded? no secrets? on-topic?

Each returns a small {ok, note} written under state["guardrail"], so the UI can
show every check as it fires.
"""

import re

from pydantic import BaseModel, Field

from .llm import get_fast_llm
from .prompts import EXEC_GUARD, INPUT_GUARD, OUTPUT_GUARD
from .state import ReviewState

# A GitHub repo URL looks like https://github.com/<owner>/<name>.
_GITHUB_URL = re.compile(r"https?://github\.com/[\w.-]+/[\w.-]+", re.IGNORECASE)


class GuardResult(BaseModel):
    """Shared shape for every guardrail decision."""

    ok: bool = Field(description="true if the check passes, false to flag/block")
    note: str = Field(description="one short line explaining the decision")


async def input_guardrail(state: ReviewState) -> dict:
    repo_url = state.get("repo_url", "") or ""
    user_query = state.get("user_query", "") or ""

    # Cheap pre-check before spending an LLM call.
    if not _GITHUB_URL.search(repo_url):
        return {"guardrail": {"input": {"ok": False, "note": "No valid GitHub repository URL provided."}}}

    llm = get_fast_llm().with_structured_output(GuardResult)
    result = await llm.ainvoke([
        ("system", INPUT_GUARD),
        ("human", f"Repo URL: {repo_url}\nUser request: {user_query or '(none provided)'}"),
    ])
    return {"guardrail": {"input": result.model_dump()}}


def execution_guardrail(agent_name: str):
    """Factory: the FIRST node of an agent subgraph. Pre-flight before tools run."""

    async def _node(state: ReviewState) -> dict:
        if agent_name not in state.get("selected_agents", []):
            return {}  # not selected → no-op, fast.

        repo_url = state.get("repo_url", "") or ""
        llm = get_fast_llm().with_structured_output(GuardResult)
        result = await llm.ainvoke([
            ("system", EXEC_GUARD),
            ("human", f"Agent: {agent_name}\nRepo: {repo_url}\nPlanned action: read-only inspection via the GitHub MCP server."),
        ])
        return {"guardrail": {f"execution_{agent_name}": result.model_dump()}}

    return _node


async def output_guardrail(state: ReviewState) -> dict:
    findings = state.get("findings", {})
    summary = state.get("summary", "") or ""

    llm = get_fast_llm().with_structured_output(GuardResult)
    result = await llm.ainvoke([
        ("system", OUTPUT_GUARD),
        ("human", f"Agent findings: {findings}\n\nProposed summary: {summary}"),
    ])
    return {"guardrail": {"output": result.model_dump()}}
