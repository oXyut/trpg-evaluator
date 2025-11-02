from __future__ import annotations

import random
import uuid
import os
from pathlib import Path
from typing import Dict, Optional

from app.schemas.character import (
    CharacterCreateRequest,
    CharacterDerived,
    CharacterMethod,
    CharacterMeta,
    CharacterModel,
    CharacterStats,
    CharacterUpdateRequest,
    ImportPayload,
    PointBuyPayload,
    RandomCharacterOptions,
)
from app.services.storage import JSONBackedCollection


class InMemoryCharacterRepository:
    def __init__(self) -> None:
        self._items: Dict[str, CharacterModel] = {}

    def list(self) -> list[CharacterModel]:
        return list(self._items.values())

    def get(self, character_id: str) -> Optional[CharacterModel]:
        return self._items.get(character_id)

    def save(self, model: CharacterModel) -> CharacterModel:
        self._items[model.id] = model
        return model

    def update(self, character_id: str, data: CharacterUpdateRequest) -> Optional[CharacterModel]:
        model = self._items.get(character_id)
        if model is None:
            return None

        update_payload = {}
        if data.pc_name is not None:
            update_payload["pc_name"] = data.pc_name
        if data.meta is not None:
            update_payload["meta"] = data.meta
        if data.stats is not None:
            update_payload["stats"] = data.stats
            update_payload["derived"] = compute_derived(data.stats, luck=model.derived.Luck)
        if data.skills is not None:
            update_payload["skills"] = data.skills
        if data.inventory is not None:
            update_payload["inventory"] = data.inventory

        updated = model.model_copy(update=update_payload)
        self._items[character_id] = updated
        return updated


class FileCharacterRepository(InMemoryCharacterRepository):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self._collection = JSONBackedCollection[
            CharacterModel
        ](
            path,
            serializer=lambda item: item.model_dump(),
            deserializer=lambda data: CharacterModel.model_validate(data),
        )
        for model in self._collection:
            self._items[model.id] = CharacterRecord(model=model)

    def _persist(self) -> None:
        snapshot = [record.model for record in self._items.values()]
        self._collection.replace_items(snapshot)

    def save(self, model: CharacterModel) -> CharacterModel:
        result = super().save(model)
        self._persist()
        return result

    def update(self, character_id: str, data: CharacterUpdateRequest) -> Optional[CharacterModel]:
        updated = super().update(character_id, data)
        if updated is not None:
            self._persist()
        return updated


def _create_repository() -> InMemoryCharacterRepository:
    path = os.getenv("CHARACTER_STORE_PATH")
    if path:
        return FileCharacterRepository(Path(path))
    return InMemoryCharacterRepository()


repository = _create_repository()


def create_character(payload: CharacterCreateRequest) -> CharacterModel:
    if payload.method == CharacterMethod.random.value:
        model = generate_random_character(payload.random_options or RandomCharacterOptions())
    elif payload.method == CharacterMethod.point_buy.value:
        model = create_point_buy_character(payload.point_buy)
    else:
        model = create_import_character(payload.import_data)
    return repository.save(model)


def generate_random_character(options: RandomCharacterOptions) -> CharacterModel:
    stats = CharacterStats(
        STR=roll_stat(),
        CON=roll_stat(),
        SIZ=roll_stat(high=True),
        DEX=roll_stat(),
        APP=roll_stat(),
        INT=roll_stat(high=True),
        POW=roll_stat(),
        EDU=roll_stat(high=True),
    )
    pc_name = options.name_hint or f"Investigator {random.randint(100, 999)}"
    character_id = generate_character_id()
    derived = compute_derived(stats)
    meta = CharacterMeta(era=options.era, profession=options.profession)
    skills = {
        "Listen": 20,
        "Spot Hidden": 25,
        "Library Use": 20,
    }
    return CharacterModel(
        id=character_id,
        pc_name=pc_name,
        meta=meta,
        stats=stats,
        derived=derived,
        skills=skills,
        inventory=[],
    )


def roll_stat(high: bool = False) -> int:
    if high:
        return (sum(random.randint(1, 6) for _ in range(2)) + 6) * 5
    return sum(random.randint(1, 6) for _ in range(3)) * 5


def compute_derived(stats: CharacterStats, *, luck: Optional[int] = None) -> CharacterDerived:
    hp = max(1, (stats.CON + stats.SIZ) // 10)
    mp = max(1, stats.POW // 5)
    san = stats.POW * 5
    generated_luck = luck if luck is not None else sum(random.randint(1, 6) for _ in range(3)) * 5
    build, db = compute_build_and_db(stats)
    move = compute_move(stats)
    return CharacterDerived(
        HP=hp,
        MP=mp,
        SAN=san,
        Luck=generated_luck,
        Build=build,
        DB=db,
        Move=move,
    )


def compute_build_and_db(stats: CharacterStats) -> tuple[int, str]:
    total = stats.STR + stats.SIZ
    if total <= 64:
        return -2, "-2d6"
    if total <= 84:
        return -1, "-1d4"
    if total <= 124:
        return 0, "+0"
    if total <= 164:
        return 1, "+1d4"
    if total <= 204:
        return 2, "+1d6"
    return 3, "+2d6"


def compute_move(stats: CharacterStats) -> int:
    if stats.DEX < stats.SIZ and stats.STR < stats.SIZ:
        return 7
    if stats.DEX > stats.SIZ and stats.STR > stats.SIZ:
        return 9
    return 8


def create_point_buy_character(payload: Optional[PointBuyPayload]) -> CharacterModel:
    if payload is None:
        raise ValueError("point_buy payload is required for point_buy method")
    character_id = generate_character_id()
    derived = compute_derived(payload.stats)
    return CharacterModel(
        id=character_id,
        pc_name=payload.pc_name,
        meta=payload.meta,
        stats=payload.stats,
        derived=derived,
        skills=payload.skills,
        inventory=payload.inventory,
    )


def create_import_character(payload: Optional[ImportPayload]) -> CharacterModel:
    if payload is None:
        raise ValueError("import_data payload is required for import method")
    model = payload.model_copy()
    if not model.id:
        model.id = generate_character_id()
    return model


def generate_character_id() -> str:
    return f"pc_{uuid.uuid4().hex[:8]}"


def to_snapshot(model: CharacterModel) -> Dict[str, object]:
    key_skills = dict(sorted(model.skills.items(), key=lambda item: item[1], reverse=True)[:3])
    return {
        "id": model.id,
        "pc_name": model.pc_name,
        "era": model.meta.era if model.meta else None,
        "profession": model.meta.profession if model.meta else None,
        "HP": model.derived.HP,
        "MP": model.derived.MP,
        "SAN": model.derived.SAN,
        "key_skills": key_skills,
    }
