from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.character import (
    CharacterCreateRequest,
    CharacterResponse,
    CharacterUpdateRequest,
    SnapshotResponse,
)
from app.services import characters

router = APIRouter(prefix="/v1/characters", tags=["characters"])


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(request: CharacterCreateRequest):
    model = characters.create_character(request)
    return CharacterResponse.model_validate(model)


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: str):
    model = characters.repository.get(character_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return CharacterResponse.model_validate(model)


@router.patch("/{character_id}", response_model=CharacterResponse)
def update_character(character_id: str, request: CharacterUpdateRequest):
    model = characters.repository.update(character_id, request)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return CharacterResponse.model_validate(model)


@router.get("/{character_id}/snapshot", response_model=SnapshotResponse)
def get_snapshot(character_id: str):
    model = characters.repository.get(character_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    snapshot = characters.to_snapshot(model)
    return SnapshotResponse.model_validate(snapshot)
