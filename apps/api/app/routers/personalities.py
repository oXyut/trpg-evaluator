from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.personality import PersonalityResponse, PersonalityUpsertRequest
from app.services import characters, personalities

router = APIRouter(prefix="/v1/personalities", tags=["personalities"])


@router.put("/{character_id}", response_model=PersonalityResponse)
def upsert_personality(character_id: str, request: PersonalityUpsertRequest):
    character = characters.repository.get(character_id)
    if character is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return personalities.repository.upsert(character_id, request)


@router.get("/{character_id}", response_model=PersonalityResponse)
def get_personality(character_id: str):
    response = personalities.repository.get(character_id)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personality not found")
    return response
