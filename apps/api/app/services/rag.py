from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.schemas.scenario import ScenarioModel


@dataclass
class RAGMatch:
    chunk_id: str
    score: float
    content: str


def simple_retrieve(query: str, scenario: ScenarioModel, *, top_k: int = 3) -> List[RAGMatch]:
    if not scenario.chunks:
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
    return matches[:top_k]
