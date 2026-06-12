"""The non-agent nodes of the main graph.

FAST model: reformulation, tone of voice.
SMART model: orchestrator, summarizer, evaluation.
"""

from pydantic import BaseModel, Field

from .llm import get_fast_llm, get_smart_llm
from .prompts import (
    EVALUATION_PROMPT,
    ORCHESTRATOR_PROMPT,
    REFORMULATION_PROMPT,
    SUMMARIZER_PROMPT,
    TONE_PROMPT,
)
from .state import ReviewState

ALLOWED_AGENTS = ["structure", "readme", "test"]


class Reformulated(BaseModel):
    reformulated_query: str = Field(description="one clear sentence describing what to review")
    repo_url: str = Field(description="the GitHub repo URL found in the query, or '' if none")


class Orchestration(BaseModel):
    selected_agents: list[str] = Field(description="subset of: structure, readme, test")
    reasoning: str = Field(description="one-line reason for the choice")


class Evaluation(BaseModel):
    score: int = Field(description="overall quality of the review, 1 (poor) to 5 (excellent)")
    justification: str = Field(description="one-line justification for the score")


async def query_reformulation(state: ReviewState) -> dict:
    user_query = state.get("user_query", "") or ""
    repo_url = state.get("repo_url", "") or ""

    llm = get_fast_llm().with_structured_output(Reformulated)
    result = await llm.ainvoke([
        ("system", REFORMULATION_PROMPT),
        ("human", f"Repo URL: {repo_url or '(none)'}\nRaw query: {user_query or '(none)'}"),
    ])
    # Trust the URL the user gave us; only fall back to the extracted one.
    return {
        "reformulated_query": result.reformulated_query,
        "repo_url": repo_url or result.repo_url,
    }


async def orchestrator(state: ReviewState) -> dict:
    request = state.get("reformulated_query") or state.get("user_query") or ""

    llm = get_smart_llm().with_structured_output(Orchestration)
    result = await llm.ainvoke([
        ("system", ORCHESTRATOR_PROMPT),
        ("human", f"Request: {request}\nRepo: {state.get('repo_url', '')}"),
    ])

    selected = [a for a in result.selected_agents if a in ALLOWED_AGENTS]
    if not selected:
        selected = list(ALLOWED_AGENTS)  # default: run all three.

    return {
        "selected_agents": selected,
        "guardrail": {"orchestrator": {"selected": selected, "reasoning": result.reasoning}},
    }


async def summarizer(state: ReviewState) -> dict:
    findings = state.get("findings", {})
    llm = get_smart_llm()
    resp = await llm.ainvoke([
        ("system", SUMMARIZER_PROMPT),
        ("human", f"Agent findings to summarise:\n{findings}"),
    ])
    return {"summary": resp.content}


async def answer_evaluation(state: ReviewState) -> dict:
    findings = state.get("findings", {})
    summary = state.get("summary", "") or ""
    llm = get_smart_llm().with_structured_output(Evaluation)
    result = await llm.ainvoke([
        ("system", EVALUATION_PROMPT),
        ("human", f"Findings: {findings}\n\nSummary under review:\n{summary}"),
    ])
    return {"evaluation": result.model_dump()}


async def tone_of_voice(state: ReviewState) -> dict:
    llm = get_fast_llm()
    input_guard = state.get("guardrail", {}).get("input", {})

    # Refusal path: input guardrail blocked the request.
    if input_guard and not input_guard.get("ok", True):
        note = input_guard.get("note", "the request could not be processed")
        resp = await llm.ainvoke([
            ("system", TONE_PROMPT),
            ("human", f"Politely decline this code-review request in one or two friendly sentences. Reason: {note}"),
        ])
        return {"final_answer": resp.content}

    # Normal path: polish the summary.
    summary = state.get("summary", "") or ""
    resp = await llm.ainvoke([
        ("system", TONE_PROMPT),
        ("human", f"Rewrite this repository review for the user:\n\n{summary}"),
    ])
    return {"final_answer": resp.content}
