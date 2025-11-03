from __future__ import annotations

from enum import Enum
from typing import Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, conint, field_validator, model_validator


STAT_NAMES = ("STR", "CON", "SIZ", "DEX", "APP", "INT", "POW", "EDU")
SkillValue = conint(ge=0, le=99)  # type: ignore


class CharacterMethod(str, Enum):
    random = "random"
    point_buy = "point_buy"
    import_ = "import"


class CharacterStats(BaseModel):
    STR: int = Field(..., ge=5, le=99)
    CON: int = Field(..., ge=5, le=99)
    SIZ: int = Field(..., ge=5, le=99)
    DEX: int = Field(..., ge=5, le=99)
    APP: int = Field(..., ge=5, le=99)
    INT: int = Field(..., ge=5, le=99)
    POW: int = Field(..., ge=5, le=99)
    EDU: int = Field(..., ge=5, le=99)


class CharacterDerived(BaseModel):
    HP: int
    MP: int
    SAN: int
    Luck: int
    Build: int
    DB: str
    Move: int


class CharacterMeta(BaseModel):
    era: Optional[str] = None
    profession: Optional[str] = None


class CharacterModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    pc_name: str
    meta: CharacterMeta = Field(default_factory=CharacterMeta)
    stats: CharacterStats
    derived: CharacterDerived
    skills: Dict[str, SkillValue] = Field(default_factory=dict)
    inventory: list[str] = Field(default_factory=list)


class CharacterSnapshot(BaseModel):
    id: str
    pc_name: str
    era: Optional[str]
    profession: Optional[str]
    HP: int
    MP: int
    SAN: int
    key_skills: Dict[str, int]


class RandomCharacterOptions(BaseModel):
    name_hint: Optional[str] = None
    era: Optional[str] = None
    profession: Optional[str] = None


class PointBuyPayload(BaseModel):
    pc_name: str
    stats: CharacterStats
    skills: Dict[str, SkillValue] = Field(default_factory=dict)
    meta: CharacterMeta = Field(default_factory=CharacterMeta)
    inventory: list[str] = Field(default_factory=list)


class ImportPayload(CharacterModel):
    pass


class CharacterCreateRequest(BaseModel):
    method: Literal["random", "point_buy", "import"]
    random_options: Optional[RandomCharacterOptions] = None
    point_buy: Optional[PointBuyPayload] = None
    import_data: Optional[ImportPayload] = None

    @model_validator(mode="after")
    def ensure_payloads(self) -> "CharacterCreateRequest":
        if self.method == CharacterMethod.random.value:
            if self.random_options is None:
                self.random_options = RandomCharacterOptions()
        elif self.method == CharacterMethod.point_buy.value:
            if self.point_buy is None:
                raise ValueError("point_buy payload required for point_buy method")
        elif self.method == CharacterMethod.import_.value:
            if self.import_data is None:
                raise ValueError("import_data payload required for import method")
        return self


class CharacterUpdateRequest(BaseModel):
    pc_name: Optional[str] = None
    stats: Optional[CharacterStats] = None
    skills: Optional[Dict[str, SkillValue]] = None
    meta: Optional[CharacterMeta] = None
    inventory: Optional[list[str]] = None


class CharacterListResponse(BaseModel):
    items: list[CharacterModel]


class CharacterResponse(CharacterModel):
    pass


class SnapshotResponse(CharacterSnapshot):
    pass
