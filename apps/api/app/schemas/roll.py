from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class RollRequest(BaseModel):
    expr: str = Field(default="1d100")
    bonus: int = Field(default=0, ge=-2, le=2)
    skill: int = Field(ge=1, le=99)

    @field_validator("expr")
    @classmethod
    def validate_expr(cls, value: str) -> str:
        if value != "1d100":
            raise ValueError("Only 1d100 expressions are supported in MVP")
        return value


class RollResult(BaseModel):
    expr: str
    rolls: List[int]
    total: int
    result: str
    thresholds: Dict[str, int]
