"""Structure agent — judges the repo's folder layout and separation of concerns."""

from typing import Literal

from pydantic import BaseModel, Field

from ..prompts import STRUCTURE_ANALYZE, STRUCTURE_SELECT
from ._common import build_agent_subgraph


class StructureVerdict(BaseModel):
    verdict: Literal["good", "needs_work"]
    reasons: list[str] = Field(description="short bullet reasons for the verdict")
    evidence: list[str] = Field(description="file/folder names you actually saw")


structure_agent = build_agent_subgraph(
    "structure", STRUCTURE_SELECT, STRUCTURE_ANALYZE, StructureVerdict
)
