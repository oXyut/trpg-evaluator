"""Dice rolling utilities for Call of Cthulhu 7th edition style d100 rolls."""
from __future__ import annotations

from dataclasses import dataclass
from random import randint
from typing import List


@dataclass
class DiceRollResult:
    expr: str
    rolls: List[int]
    total: int


def roll_d100(bonus: int = 0) -> DiceRollResult:
    """Roll a d100 with optional bonus/penalty dice.

    Args:
        bonus: Positive values indicate bonus dice, negative values represent penalty dice.

    Returns:
        DiceRollResult containing raw rolls (tens dice plus ones) and the selected total value.
    """
    ones = randint(0, 9)
    base_tens = randint(0, 9)
    candidates = []

    def compute_total(tens: int) -> int:
        value = tens * 10 + ones
        return 100 if value == 0 else value

    candidates.append(compute_total(base_tens))

    for _ in range(abs(bonus)):
        extra_tens = randint(0, 9)
        candidates.append(compute_total(extra_tens))

    if bonus > 0:
        total = min(candidates)
    elif bonus < 0:
        total = max(candidates)
    else:
        total = candidates[0]

    return DiceRollResult(expr="1d100", rolls=candidates, total=total)


def resolve_success(total: int, skill: int) -> str:
    """Return success tier for a d100 roll."""
    if total <= max(1, skill // 5):
        return "Extreme"
    if total <= max(1, skill // 2):
        return "Hard"
    if total <= skill:
        return "Success"
    return "Fail"


def thresholds_for_skill(skill: int) -> dict[str, int]:
    return {
        "regular": skill,
        "hard": max(1, skill // 2),
        "extreme": max(1, skill // 5),
    }
