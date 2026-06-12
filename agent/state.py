"""The shared state for the whole review.

ONE TypedDict is used by the main graph AND every agent subgraph, so values
flow straight through. `findings` and `guardrail` are written by several nodes,
so they use a dict-merge reducer instead of last-write-wins (which would clobber
earlier writes).
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


def merge_dicts(left: dict, right: dict) -> dict:
    """Reducer: shallow-merge dict updates from multiple nodes."""
    return {**(left or {}), **(right or {})}


class ReviewState(TypedDict, total=False):
    user_query: str                          # the raw question the user typed
    repo_url: str                            # the GitHub repo under review
    reformulated_query: str                  # cleaned-up task for the agents
    selected_agents: list[str]               # which agents the orchestrator picked
    findings: Annotated[dict, merge_dicts]   # per-agent: {verdict, reasons, evidence}
    summary: str                             # merged natural-language summary
    evaluation: dict                         # {score: 1-5, justification}
    final_answer: str                        # tone-polished answer shown to the user
    guardrail: Annotated[dict, merge_dicts]  # flags/notes from input/exec/output guards
    messages: Annotated[list, add_messages]  # tool-call traffic inside subgraphs
