from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.schemas.scenario import ScenarioModel


@dataclass
class AgentTurn:
    actor: str
    content: str
    references: List[str]


def orchestrate_session(*, scenario: ScenarioModel, actors: List[str], max_turns: int) -> List[AgentTurn]:
    turns: List[AgentTurn] = []
    char_count = len(actors)
    for index in range(max_turns):
        actor = actors[index % char_count]
        chunk = scenario.chunks[index % len(scenario.chunks)] if scenario and scenario.chunks else None
        text = chunk.content if chunk else "シナリオ参照なし"
        if actor == "Keeper":
            content = f"Keeper提示: {text[:180]}"
        else:
            content = f"{actor}の宣言: {text[:120]} を踏まえた行動"
        references = [f"{scenario.id}#{chunk.id}"] if chunk else []
        turns.append(AgentTurn(actor=actor, content=content, references=references))
    return turns
