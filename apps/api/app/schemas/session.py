from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SessionCreateRequest(BaseModel):
    scenario_id: str
    party_ids: List[str] = Field(..., min_length=1)
    seed: Optional[int] = None
    max_turns: int = Field(default=10, ge=1, le=100)


class SessionResponse(BaseModel):
    id: str
    scenario_id: str
    party_ids: List[str]
    created_at: datetime
    status: str
    max_turns: int


class SessionTurn(BaseModel):
    turn_index: int
    actor: str
    role: str
    content: str
    references: List[str] = Field(default_factory=list)


class TurnsResponse(BaseModel):
    session_id: str
    items: List[SessionTurn]
    next_cursor: Optional[int]


class FeedbackMetric(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    comment: str


class SessionFeedback(BaseModel):
    session_id: str
    summary: str
    metrics: Dict[str, FeedbackMetric]

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: Dict[str, FeedbackMetric]) -> Dict[str, FeedbackMetric]:
        required = {"pacing", "branching", "difficulty", "fairness", "cohesion", "tone"}
        missing = required.difference(value.keys())
        if missing:
            raise ValueError(f"Missing metrics: {', '.join(sorted(missing))}")
        return value
