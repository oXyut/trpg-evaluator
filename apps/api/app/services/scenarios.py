from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from app.schemas.scenario import (
    ScenarioCreateRequest,
    ScenarioChunk,
    ScenarioModel,
    ScenarioQueryRequest,
    ScenarioQueryResponse,
    ScenarioQueryResult,
    ScenarioResponse,
)


PARAGRAPH_SPLIT_PATTERN = re.compile(r"\n{2,}")


@dataclass
class ScenarioRecord:
    model: ScenarioModel


class InMemoryScenarioRepository:
    def __init__(self) -> None:
        self._items: Dict[str, ScenarioRecord] = {}

    def list(self) -> List[ScenarioModel]:
        return [record.model for record in self._items.values()]

    def get(self, scenario_id: str) -> Optional[ScenarioModel]:
        record = self._items.get(scenario_id)
        return record.model if record else None

    def save(self, model: ScenarioModel) -> ScenarioModel:
        self._items[model.id] = ScenarioRecord(model=model)
        return model


def generate_scenario_id() -> str:
    return f"scn_{uuid.uuid4().hex[:8]}"


def chunk_content(content: str, *, chunk_size: int) -> List[str]:
    paragraphs = [para.strip() for para in PARAGRAPH_SPLIT_PATTERN.split(content) if para.strip()]
    if not paragraphs:
        return [content.strip()]

    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    for para in paragraphs:
        paragraph_len = len(para)
        if current_len + paragraph_len + 1 > chunk_size and current:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += paragraph_len + 2

    if current:
        chunks.append("\n\n".join(current))
    return chunks
class FileScenarioRepository(InMemoryScenarioRepository):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        data = json.loads(self._path.read_text())
        for entry in data:
            model = ScenarioModel.model_validate(entry)
            self._items[model.id] = ScenarioRecord(model=model)

    def _persist(self) -> None:
        payload = [record.model.model_dump() for record in self._items.values()]
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    def save(self, model: ScenarioModel) -> ScenarioModel:
        result = super().save(model)
        self._persist()
        return result


def _create_repository() -> InMemoryScenarioRepository:
    path = os.getenv("SCENARIO_STORE_PATH")
    if path:
        return FileScenarioRepository(Path(path))
    return InMemoryScenarioRepository()


repository = _create_repository()


def create_scenario(payload: ScenarioCreateRequest) -> ScenarioResponse:
    scenario_id = generate_scenario_id()
    chunk_texts = chunk_content(payload.content, chunk_size=payload.chunk_size)
    chunks = [
        ScenarioChunk(id=f"chunk_{index+1}", order=index, content=text)
        for index, text in enumerate(chunk_texts)
    ]
    model = ScenarioModel(
        id=scenario_id,
        name=payload.name,
        source_type=payload.source_type,
        content=payload.content,
        chunks=chunks,
    )
    repository.save(model)
    return ScenarioResponse.model_validate(model)


def list_scenarios() -> List[ScenarioResponse]:
    return [ScenarioResponse.model_validate(item) for item in repository.list()]


def get_scenario(scenario_id: str) -> Optional[ScenarioResponse]:
    model = repository.get(scenario_id)
    if model is None:
        return None
    return ScenarioResponse.model_validate(model)


def query_scenario(scenario_id: str, payload: ScenarioQueryRequest) -> Optional[ScenarioQueryResponse]:
    model = repository.get(scenario_id)
    if model is None:
        return None

    matches: List[ScenarioQueryResult] = []
    query_lower = payload.query.lower()
    for chunk in model.chunks:
        content_lower = chunk.content.lower()
        occurrences = content_lower.count(query_lower)
        if occurrences > 0:
            score = occurrences / max(len(content_lower), 1)
            matches.append(
                ScenarioQueryResult(
                    chunk_id=chunk.id,
                    score=score,
                    content=chunk.content,
                )
            )

    matches.sort(key=lambda result: result.score, reverse=True)
    matches = matches[: payload.top_k]
    return ScenarioQueryResponse(scenario_id=scenario_id, matches=matches)
