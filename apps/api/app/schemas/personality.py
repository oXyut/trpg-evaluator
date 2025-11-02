from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class PersonalityVector(BaseModel):
    risk_taking: float = Field(ge=0.0, le=1.0)
    cooperation: float = Field(ge=0.0, le=1.0)
    curiosity: float = Field(ge=0.0, le=1.0)
    violence_avoidance: float = Field(ge=0.0, le=1.0)


class PersonalityUpsertRequest(BaseModel):
    vector: PersonalityVector


class PersonalityResponse(BaseModel):
    character_id: str
    vector: PersonalityVector


class PersonalityRepositoryRecord(BaseModel):
    character_id: str
    vector: PersonalityVector

    def to_response(self) -> PersonalityResponse:
        return PersonalityResponse(character_id=self.character_id, vector=self.vector)
