from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Finding(BaseModel):
    statement: str
    evidence: list[str]
    confidence: Literal["low", "medium", "high"]


class ProposedChange(BaseModel):
    factor: str
    current: str | float | None
    proposal: str | float
    rationale: str
    risk: str
    expected_effect: str


class NextRoundDesign(BaseModel):
    design_type: Literal["screening", "fractional", "lhs"]
    factors: dict[str, list[str | float]]
    runs: int
    notes: str


class DecisionCard(BaseModel):
    project_id: str
    experiment_id: str
    summary: str
    key_findings: list[Finding]
    proposed_changes: list[ProposedChange]
    next_design: NextRoundDesign | None
    references: list[str]


