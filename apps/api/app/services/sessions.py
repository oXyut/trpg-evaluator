from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.schemas.session import (
    FeedbackMetric,
    SessionCreateRequest,
    SessionFeedback,
    SessionResponse,
    SessionTurn,
    TurnsResponse,
)
from app.services import scenarios as scenario_service


@dataclass
class SessionRecord:
    response: SessionResponse
    turns: List[SessionTurn] = field(default_factory=list)
    feedback: Optional[SessionFeedback] = None


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._items: Dict[str, SessionRecord] = {}

    def create(self, payload: SessionCreateRequest) -> SessionResponse:
        session_id = f"sess_{random.randint(1_000_000, 9_999_999)}"
        created = SessionResponse(
            id=session_id,
            scenario_id=payload.scenario_id,
            party_ids=payload.party_ids,
            created_at=datetime.now(timezone.utc),
            status="completed",
            max_turns=payload.max_turns,
        )
        scenario = scenario_service.repository.get(payload.scenario_id)
        generator = SessionGenerator(seed=payload.seed, max_turns=payload.max_turns, scenario=scenario)
        turns = generator.generate_turns(party_ids=payload.party_ids)
        feedback = generator.generate_feedback(session_id)
        self._items[session_id] = SessionRecord(response=created, turns=turns, feedback=feedback)
        return created

    def get_turns(self, session_id: str, cursor: Optional[int], limit: int = 5) -> Optional[TurnsResponse]:
        record = self._items.get(session_id)
        if record is None:
            return None
        start = cursor or 0
        end = min(start + limit, len(record.turns))
        items = record.turns[start:end]
        next_cursor = end if end < len(record.turns) else None
        return TurnsResponse(session_id=session_id, items=items, next_cursor=next_cursor)

    def get_feedback(self, session_id: str) -> Optional[SessionFeedback]:
        record = self._items.get(session_id)
        if record is None:
            return None
        return record.feedback


class SessionGenerator:
    def __init__(self, seed: Optional[int], max_turns: int, scenario: Optional[scenario_service.ScenarioModel]) -> None:
        self.random = random.Random(seed)
        self.max_turns = max_turns
        self.scenario = scenario

    def generate_turns(self, party_ids: List[str]) -> List[SessionTurn]:
        actors = ["Keeper"] + party_ids
        turns: List[SessionTurn] = []
        for index in range(self.max_turns):
            actor = actors[index % len(actors)]
            role = "Keeper" if actor == "Keeper" else "Player"
            content = self._generate_content(actor, index)
            references = self._generate_references(index)
            turns.append(
                SessionTurn(
                    turn_index=index,
                    actor=actor,
                    role=role,
                    content=content,
                    references=references,
                )
            )
        return turns

    def _generate_content(self, actor: str, turn_index: int) -> str:
        if actor == "Keeper":
            return f"Keeper describes eerie development at turn {turn_index}."
        return f"{actor} declares an action informed by prior clues at turn {turn_index}."

    def _generate_references(self, turn_index: int) -> List[str]:
        if self.scenario and self.scenario.chunks:
            chunk = self.scenario.chunks[turn_index % len(self.scenario.chunks)]
            return [f"{self.scenario.id}#{chunk.id}"]
        if turn_index % 2 == 0:
            return [f"scenario#paragraph_{turn_index % 3}"]
        return []

    def generate_feedback(self, session_id: str) -> SessionFeedback:
        metrics = {
            "pacing": self._metric("Steady escalation with brief lulls."),
            "branching": self._metric("Multiple clues offered meaningful choices."),
            "difficulty": self._metric("Skill checks landed around 60% success rate."),
            "fairness": self._metric("Consequences telegraphed ahead of time."),
            "cohesion": self._metric("Narrative remained consistent across turns."),
            "tone": self._metric("Horror tone preserved with occasional levity."),
        }
        summary = "Session reached climax within allotted turns and delivered actionable notes."
        return SessionFeedback(session_id=session_id, summary=summary, metrics=metrics)

    def _metric(self, comment: str) -> FeedbackMetric:
        score = round(self.random.uniform(0.5, 0.95), 2)
        return FeedbackMetric(score=score, comment=comment)


def create_session(payload: SessionCreateRequest) -> SessionResponse:
    return repository.create(payload)


def get_turns(session_id: str, cursor: Optional[int]) -> Optional[TurnsResponse]:
    return repository.get_turns(session_id, cursor)


def get_feedback(session_id: str) -> Optional[SessionFeedback]:
    return repository.get_feedback(session_id)


repository = InMemorySessionRepository()
