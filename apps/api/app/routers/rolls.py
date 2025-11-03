from __future__ import annotations

from fastapi import APIRouter

from app.schemas.roll import RollRequest, RollResult
from app.utils.dice import resolve_success, thresholds_for_skill, roll_d100

router = APIRouter(prefix="/v1/rolls", tags=["rolls"])


@router.post("", response_model=RollResult)
def roll(request: RollRequest):
    dice = roll_d100(bonus=request.bonus)
    thresholds = thresholds_for_skill(request.skill)
    result = resolve_success(dice.total, request.skill)
    return RollResult(
        expr=request.expr,
        rolls=dice.rolls,
        total=dice.total,
        result=result,
        thresholds=thresholds,
    )
