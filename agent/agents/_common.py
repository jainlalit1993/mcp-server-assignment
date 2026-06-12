"""Shared machinery for the three agent subgraphs.

Every agent is the SAME little pipeline:

    START -> execution_guardrail -> tool_selection -> tool_execution -> analyze -> END

Only the prompts and the verdict shape change, so the mechanics live here once.
Each node no-ops fast if its agent wasn't selected, which keeps the main graph
static and easy to draw in Studio.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph

from ..guardrails import execution_guardrail
from ..llm import get_smart_llm
from ..mcp_client import get_github_tools
from ..state import ReviewState


def _recent_tool_data(messages: list) -> str:
    """Collect the ToolMessages from the most recent tool-calling turn.

    Agents run one after another and share the messages channel, so we walk back
    from the end and stop at the AIMessage that requested these tools — that gives
    us exactly the current agent's tool results.
    """
    collected = []
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            collected.append(str(msg.content))
        elif isinstance(msg, AIMessage) and msg.tool_calls:
            break
    return "\n\n".join(reversed(collected))


def _make_tool_selection(agent_name: str, select_prompt: str):
    """LLM picks which GitHub MCP tools to call for this repo."""

    async def tool_selection(state: ReviewState) -> dict:
        if agent_name not in state.get("selected_agents", []):
            return {}
        tools = await get_github_tools()
        llm = get_smart_llm().bind_tools(tools)
        msg = await llm.ainvoke([
            SystemMessage(select_prompt),
            HumanMessage(f"Repository: {state.get('repo_url', '')}"),
        ])
        return {"messages": [msg]}

    return tool_selection


def _make_tool_execution(agent_name: str):
    """Run the tools the LLM chose and collect their raw output."""

    async def tool_execution(state: ReviewState) -> dict:
        if agent_name not in state.get("selected_agents", []):
            return {}
        tools = await get_github_tools()
        by_name = {t.name: t for t in tools}

        last = state["messages"][-1]
        tool_calls = getattr(last, "tool_calls", None) or []
        results = []
        for call in tool_calls:
            tool = by_name.get(call["name"])
            try:
                if tool is None:
                    output = f"(tool '{call['name']}' is not available)"
                else:
                    output = await tool.ainvoke(call["args"])
            except Exception as exc:
                # A failed read is itself evidence (e.g. a missing README).
                output = f"ERROR calling {call['name']}: {exc}"
            results.append(ToolMessage(content=str(output), tool_call_id=call["id"]))
        return {"messages": results}

    return tool_execution


def _make_analyze(agent_name: str, analyze_prompt: str, verdict_model):
    """LLM reasons over the tool results into a verdict + reasons + evidence."""

    async def analyze(state: ReviewState) -> dict:
        if agent_name not in state.get("selected_agents", []):
            return {}
        data = _recent_tool_data(state.get("messages", []))
        llm = get_smart_llm().with_structured_output(verdict_model)
        result = await llm.ainvoke([
            SystemMessage(analyze_prompt),
            HumanMessage(
                f"Repository: {state.get('repo_url', '')}\n\n"
                f"Tool results:\n{data or '(no data returned)'}"
            ),
        ])
        return {"findings": {agent_name: result.model_dump()}}

    return analyze


def build_agent_subgraph(agent_name: str, select_prompt: str, analyze_prompt: str, verdict_model):
    """Compile one agent subgraph. The execution guardrail is always the FIRST node."""
    builder = StateGraph(ReviewState)
    builder.add_node("execution_guardrail", execution_guardrail(agent_name))
    builder.add_node("tool_selection", _make_tool_selection(agent_name, select_prompt))
    builder.add_node("tool_execution", _make_tool_execution(agent_name))
    builder.add_node("analyze", _make_analyze(agent_name, analyze_prompt, verdict_model))

    builder.add_edge(START, "execution_guardrail")
    builder.add_edge("execution_guardrail", "tool_selection")
    builder.add_edge("tool_selection", "tool_execution")
    builder.add_edge("tool_execution", "analyze")
    builder.add_edge("analyze", END)
    return builder.compile()
