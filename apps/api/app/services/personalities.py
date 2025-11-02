from __future__ import annotations

from typing import Dict, Optional

from app.schemas.personality import PersonalityRepositoryRecord, PersonalityResponse, PersonalityUpsertRequest


class InMemoryPersonalityRepository:
    def __init__(self) -> None:
        self._items: Dict[str, PersonalityRepositoryRecord] = {}

    def upsert(self, character_id: str, payload: PersonalityUpsertRequest) -> PersonalityResponse:
        record = PersonalityRepositoryRecord(character_id=character_id, vector=payload.vector)
        self._items[character_id] = record
        return record.to_response()

    def get(self, character_id: str) -> Optional[PersonalityResponse]:
        record = self._items.get(character_id)
        if record is None:
            return None
        return record.to_response()


repository = InMemoryPersonalityRepository()
