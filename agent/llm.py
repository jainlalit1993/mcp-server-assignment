"""OpenAI model factories.

Teaching point: use a cheap, fast model for the guard/format nodes and a strong
model for the reasoning nodes. That is simple, cost-aware routing — no fancy
infrastructure needed.
"""

from langchain_openai import ChatOpenAI

from . import config


def get_fast_llm() -> ChatOpenAI:
    """Cheap + fast: guardrails, query reformulation, tone of voice."""
    return ChatOpenAI(
        model=config.fast_model(),
        api_key=config.openai_api_key(),
        temperature=0,
    )


def get_smart_llm() -> ChatOpenAI:
    """Strong reasoning: orchestrator, agent analysis, summarizer, evaluation."""
    return ChatOpenAI(
        model=config.smart_model(),
        api_key=config.openai_api_key(),
        temperature=0,
    )
