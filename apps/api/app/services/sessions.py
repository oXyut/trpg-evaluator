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
from app.schemas.scenario import ScenarioChunk
from app.services import agents, rag, scenarios as scenario_service
from app.utils.logging import log_event


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
        log_event(
            "session.generate.start",
            session_id=session_id,
            scenario_id=payload.scenario_id,
            party_ids=payload.party_ids,
            seed=payload.seed,
            max_turns=payload.max_turns,
        )
        turns = generator.generate_turns(party_ids=payload.party_ids)
        feedback = generator.generate_feedback(session_id)
        self._items[session_id] = SessionRecord(response=created, turns=turns, feedback=feedback)
        log_event(
            "session.generate.complete",
            session_id=session_id,
            scenario_id=payload.scenario_id,
            turn_count=len(turns),
            has_feedback=feedback is not None,
        )
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
        actors_list = ["Keeper"] + party_ids
        if self.scenario:
            agent_turns = agents.orchestrate_session(
                scenario=self.scenario,
                actors=actors_list,
                max_turns=self.max_turns,
            )
            log_event(
                "session.turns.generated",
                mode="orchestrated",
                scenario_id=self.scenario.id,
                actor_count=len(actors_list),
                max_turns=self.max_turns,
                generated=len(agent_turns),
            )
            return [
                SessionTurn(
                    turn_index=index,
                    actor=agent_turn.actor,
                    role="Keeper" if agent_turn.actor == "Keeper" else "Player",
                    content=agent_turn.content,
                    references=agent_turn.references,
                )
                for index, agent_turn in enumerate(agent_turns)
            ]

        turns: List[SessionTurn] = []
        for index in range(self.max_turns):
            actor = actors_list[index % len(actors_list)]
            role = "Keeper" if actor == "Keeper" else "Player"
            chunk = self._select_chunk(index)
            content = self._generate_content(actor, index, chunk)
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
        log_event(
            "session.turns.generated",
            mode="synthetic",
            scenario_id=self.scenario.id if self.scenario else None,
            actor_count=len(actors_list),
            max_turns=self.max_turns,
            generated=len(turns),
        )
        return turns

    def _select_chunk(self, turn_index: int) -> Optional[ScenarioChunk]:
        if self.scenario and self.scenario.chunks:
            return self.scenario.chunks[turn_index % len(self.scenario.chunks)]
        return None

    def _generate_content(self, actor: str, turn_index: int, chunk: Optional[ScenarioChunk]) -> str:
        if chunk:
            excerpt = chunk.content.strip().split("\n")[0][:160]
            if actor == "Keeper":
                hint = self._rag_hint(chunk)
                return f"Keeper引用: 『{excerpt}』 → 提示ヒント: {hint}"
            return f"{actor}は引用チャンク『{excerpt}』を踏まえた行動を宣言する。"

        if actor == "Keeper":
            return f"Keeper describes eerie development at turn {turn_index}."
        return f"{actor} declares an action informed by prior clues at turn {turn_index}."

    def _generate_references(self, turn_index: int) -> List[str]:
        chunk = self._select_chunk(turn_index)
        if self.scenario and chunk:
            return [f"{self.scenario.id}#{chunk.id}"]
        if turn_index % 2 == 0:
            return [f"scenario#paragraph_{turn_index % 3}"]
        return []

    def _rag_hint(self, chunk: ScenarioChunk) -> str:
        if not self.scenario:
            return "シナリオ参照なし"
        matches = rag.simple_retrieve(chunk.content.split("\n")[0], self.scenario, top_k=1)
        if matches:
            excerpt = matches[0].content.strip().split("\n")[0][:80]
            return f"関連チャンク『{excerpt}』"
        return "追加ヒントなし"

    def generate_feedback(self, session_id: str) -> SessionFeedback:
        context_snippet = "シナリオ参照なし"
        if self.scenario and self.scenario.chunks:
            referenced = min(self.max_turns, len(self.scenario.chunks))
            context_snippet = f"参照チャンク数: {referenced}/{len(self.scenario.chunks)}"

        metrics = {
            "pacing": self._metric("チャンク参照を交えたテンポで進行しました。"),
            "branching": self._metric("プレイヤー行動はチャンク引用により分岐の余地を示しました。"),
            "difficulty": self._metric("引用チャンクを基にしたロール難易度は妥当です。"),
            "fairness": self._metric("Keeperは引用テキストで十分な伏線を提示しました。"),
            "cohesion": self._metric("セッション内容はチャンク内容と整合しています。"),
            "tone": self._metric("チャンク由来の描写でホラー調が維持されました。"),
        }
        summary = f"{context_snippet} / シナリオとの整合性は概ね良好です。"
        log_event(
            "session.feedback.generated",
            session_id=session_id,
            scenario_id=self.scenario.id if self.scenario else None,
            context=context_snippet,
        )
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


def get_insights(session_id: str) -> Optional[dict]:
    record = repository._items.get(session_id)
    if record is None:
        return None

    scenario = scenario_service.repository.get(record.response.scenario_id)
    references: List[str] = []
    for turn in record.turns:
        references.extend(turn.references)

    rag_samples = []
    if scenario and references:
        query = "\n".join(turn.content for turn in record.turns[:3])
        rag_samples = [match.__dict__ for match in rag.simple_retrieve(query, scenario, top_k=3)]

    return {
        "session_id": session_id,
        "scenario_id": record.response.scenario_id,
        "references": references,
        "rag_samples": rag_samples,
    }


repository = InMemorySessionRepository()
