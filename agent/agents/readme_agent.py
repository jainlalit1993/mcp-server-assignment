"""README agent — judges whether the README is clear, complete, and concise."""

from typing import Literal

from pydantic import BaseModel, Field

from ..prompts import README_ANALYZE, README_SELECT
from ._common import build_agent_subgraph


class ReadmeVerdict(BaseModel):
    verdict: Literal["clear", "unclear", "missing"]
    reasons: list[str] = Field(description="short bullet reasons for the verdict")
    evidence: list[str] = Field(description="sections or lines you actually saw")


readme_agent = build_agent_subgraph(
    "readme", README_SELECT, README_ANALYZE, ReadmeVerdict
)
