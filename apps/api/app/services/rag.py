from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

from app.schemas.scenario import ScenarioModel
from app.utils.logging import log_event


@dataclass
class RAGMatch:
    chunk_id: str
    score: float
    content: str


def simple_retrieve(query: str, scenario: ScenarioModel, *, top_k: int = 3) -> List[RAGMatch]:
    started = time.perf_counter()
    if not scenario.chunks:
        log_event(
            "rag.retrieve",
            query=query,
            scenario_id=scenario.id,
            top_k=top_k,
            match_count=0,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        return []

    query_lower = query.lower()
    matches: List[RAGMatch] = []
    for chunk in scenario.chunks:
        content_lower = chunk.content.lower()
        if not query_lower:
            score = 1 / len(scenario.chunks)
        else:
            occurrences = content_lower.count(query_lower)
            if occurrences == 0:
                continue
            score = occurrences / max(len(content_lower), 1)
        matches.append(RAGMatch(chunk_id=chunk.id, score=score, content=chunk.content))

    matches.sort(key=lambda item: item.score, reverse=True)
    selected = matches[:top_k]
    log_event(
        "rag.retrieve",
        query=query,
        scenario_id=scenario.id,
        top_k=top_k,
        match_count=len(selected),
        elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
    )
    return selected
