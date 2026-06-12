"""The main graph — wires everything together and exports `graph`.

`langgraph dev` (Studio) and the FastAPI server both import this same object.

    START
     -> input_guardrail        (blocked -> tone_of_voice -> END)
     -> query_reformulation
     -> orchestrator
     -> structure_agent        (subgraph)
     -> readme_agent           (subgraph)
     -> test_agent             (subgraph)
     -> summarizer
     -> answer_evaluation
     -> output_guardrail
     -> tone_of_voice
     -> END
"""

from langgraph.graph import END, START, StateGraph

from .agents.readme_agent import readme_agent
from .agents.structure_agent import structure_agent
from .agents.test_agent import test_agent
from .guardrails import input_guardrail, output_guardrail
from .nodes import (
    answer_evaluation,
    orchestrator,
    query_reformulation,
    summarizer,
    tone_of_voice,
)
from .state import ReviewState


def route_after_input(state: ReviewState) -> str:
    """If the input guardrail blocked the request, jump straight to a safe refusal."""
    input_guard = state.get("guardrail", {}).get("input", {})
    return "blocked" if not input_guard.get("ok", True) else "continue"


builder = StateGraph(ReviewState)

# Nodes.
builder.add_node("input_guardrail", input_guardrail)
builder.add_node("query_reformulation", query_reformulation)
builder.add_node("orchestrator", orchestrator)
builder.add_node("structure_agent", structure_agent)   # subgraph
builder.add_node("readme_agent", readme_agent)         # subgraph
builder.add_node("test_agent", test_agent)             # subgraph
builder.add_node("summarizer", summarizer)
builder.add_node("answer_evaluation", answer_evaluation)
builder.add_node("output_guardrail", output_guardrail)
builder.add_node("tone_of_voice", tone_of_voice)

# Edges.
builder.add_edge(START, "input_guardrail")
builder.add_conditional_edges(
    "input_guardrail",
    route_after_input,
    {"blocked": "tone_of_voice", "continue": "query_reformulation"},
)
builder.add_edge("query_reformulation", "orchestrator")

# Agents run sequentially for a clean, readable Studio diagram.
# To fan out: replace these with orchestrator->each agent and each agent->summarizer.
builder.add_edge("orchestrator", "structure_agent")
builder.add_edge("structure_agent", "readme_agent")
builder.add_edge("readme_agent", "test_agent")
builder.add_edge("test_agent", "summarizer")

builder.add_edge("summarizer", "answer_evaluation")
builder.add_edge("answer_evaluation", "output_guardrail")
builder.add_edge("output_guardrail", "tone_of_voice")
builder.add_edge("tone_of_voice", END)

graph = builder.compile()
