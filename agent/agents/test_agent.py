"""Test agent — judges whether unit tests are written."""

from typing import Literal

from pydantic import BaseModel, Field

from ..prompts import TEST_ANALYZE, TEST_SELECT
from ._common import build_agent_subgraph


class TestVerdict(BaseModel):
    verdict: Literal["present", "partial", "missing"]
    reasons: list[str] = Field(description="short bullet reasons for the verdict")
    evidence: list[str] = Field(description="test files/config you actually saw")


test_agent = build_agent_subgraph(
    "test", TEST_SELECT, TEST_ANALYZE, TestVerdict
)
