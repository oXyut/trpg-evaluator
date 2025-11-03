from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ScenarioChunk(BaseModel):
    id: str
    order: int
    content: str


class ScenarioModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    source_type: str
    content: str
    chunks: List[ScenarioChunk]


class ScenarioCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source_type: str = Field(default="text", min_length=1)
    chunk_size: int = Field(default=800, ge=200, le=2000)


class ScenarioResponse(ScenarioModel):
    pass


class ScenarioListResponse(BaseModel):
    items: List[ScenarioResponse]


class ScenarioQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class ScenarioQueryResult(BaseModel):
    chunk_id: str
    score: float
    content: str


class ScenarioQueryResponse(BaseModel):
    scenario_id: str
    matches: List[ScenarioQueryResult]
