from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, List, Protocol, TypeVar


T = TypeVar("T")


class Serializer(Protocol[T]):
    def __call__(self, obj: T) -> dict: ...


class Deserializer(Protocol[T]):
    def __call__(self, data: dict) -> T: ...


class JSONBackedCollection(Iterable[T]):
    def __init__(
        self,
        path: Path,
        *,
        serializer: Serializer[T],
        deserializer: Deserializer[T],
    ) -> None:
        self._path = path
        self._serializer = serializer
        self._deserializer = deserializer
        self._items: List[T] = []
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw = json.loads(self._path.read_text())
        self._items = [self._deserializer(item) for item in raw]

    def _persist(self) -> None:
        payload = [self._serializer(item) for item in self._items]
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    def __iter__(self):
        return iter(self._items)

    def replace_items(self, items: List[T]) -> None:
        self._items = items
        self._persist()

    def upsert(self, item: T, *, key: Callable[[T], str]) -> None:
        key_value = key(item)
        remaining = [existing for existing in self._items if key(existing) != key_value]
        remaining.append(item)
        self.replace_items(remaining)

