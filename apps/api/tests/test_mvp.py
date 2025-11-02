from __future__ import annotations

import random
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import characters, personalities, scenarios as scenario_service, sessions
from app.utils import dice


@pytest.fixture(autouse=True)
def reset_repositories() -> Iterator[None]:
    characters.repository = characters.InMemoryCharacterRepository()
    personalities.repository._items.clear()
    sessions.repository._items.clear()
    scenario_service.repository = scenario_service.InMemoryScenarioRepository()
    yield
    characters.repository = characters.InMemoryCharacterRepository()
    personalities.repository._items.clear()
    sessions.repository._items.clear()
    scenario_service.repository = scenario_service.InMemoryScenarioRepository()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_roll_d100_bonus_selects_lowest(monkeypatch: pytest.MonkeyPatch) -> None:
    sequence = iter([5, 8, 3])

    def fake_randint(a: int, b: int) -> int:
        return next(sequence)

    monkeypatch.setattr(dice, "randint", fake_randint)

    result = dice.roll_d100(bonus=1)

    assert result.total == 35
    assert result.rolls == [85, 35]
    assert result.expr == "1d100"


def test_roll_d100_penalty_selects_highest(monkeypatch: pytest.MonkeyPatch) -> None:
    sequence = iter([0, 2, 7])

    def fake_randint(a: int, b: int) -> int:
        return next(sequence)

    monkeypatch.setattr(dice, "randint", fake_randint)

    result = dice.roll_d100(bonus=-1)

    assert result.total == 70
    assert result.rolls == [20, 70]


def test_thresholds_and_success_tiers() -> None:
    thresholds = dice.thresholds_for_skill(65)
    assert thresholds == {"regular": 65, "hard": 32, "extreme": 13}

    assert dice.resolve_success(10, 65) == "Extreme"
    assert dice.resolve_success(30, 65) == "Hard"
    assert dice.resolve_success(60, 65) == "Success"
    assert dice.resolve_success(90, 65) == "Fail"


def test_random_character_generation_consistency() -> None:
    random.seed(1234)
    options = characters.RandomCharacterOptions(
        name_hint="Alex Sterling", era="1920s", profession="Detective"
    )

    character = characters.generate_random_character(options)

    assert character.pc_name == "Alex Sterling"
    assert character.meta.era == "1920s"
    assert character.meta.profession == "Detective"
    assert set(character.skills.keys()) == {"Listen", "Spot Hidden", "Library Use"}

    expected_derived = characters.compute_derived(character.stats, luck=character.derived.Luck)
    assert character.derived.model_dump() == expected_derived.model_dump()


def test_character_lifecycle_via_api(client: TestClient) -> None:
    payload = {
        "method": "point_buy",
        "point_buy": {
            "pc_name": "Junpei Aoki",
            "stats": {
                "STR": 60,
                "CON": 55,
                "SIZ": 65,
                "DEX": 50,
                "APP": 45,
                "INT": 70,
                "POW": 60,
                "EDU": 75
            },
            "skills": {"Library Use": 60, "Spot Hidden": 55},
            "meta": {"era": "Heisei", "profession": "Journalist"},
            "inventory": ["Notebook", "Camera"]
        }
    }

    create_response = client.post("/v1/characters", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    character_id = created["id"]

    get_response = client.get(f"/v1/characters/{character_id}")
    assert get_response.status_code == 200
    assert get_response.json()["pc_name"] == "Junpei Aoki"

    patch_response = client.patch(
        f"/v1/characters/{character_id}", json={"pc_name": "Junpei Tachibana"}
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["pc_name"] == "Junpei Tachibana"

    snapshot_response = client.get(f"/v1/characters/{character_id}/snapshot")
    assert snapshot_response.status_code == 200
    snapshot = snapshot_response.json()
    assert snapshot["pc_name"] == "Junpei Tachibana"
    assert snapshot["key_skills"]


def test_personality_and_session_endpoints(client: TestClient) -> None:
    character_payload = {
        "method": "random",
        "random_options": {"name_hint": "Mina"}
    }
    char_response = client.post("/v1/characters", json=character_payload)
    character_id = char_response.json()["id"]

    personality_payload = {
        "vector": {
            "risk_taking": 0.7,
            "cooperation": 0.5,
            "curiosity": 0.9,
            "violence_avoidance": 0.6
        }
    }
    put_response = client.put(
        f"/v1/personalities/{character_id}", json=personality_payload
    )
    assert put_response.status_code == 200
    assert put_response.json()["vector"]["curiosity"] == 0.9

    get_response = client.get(f"/v1/personalities/{character_id}")
    assert get_response.status_code == 200

    session_request = {
        "scenario_id": "scenario_alpha",
        "party_ids": [character_id],
        "seed": 99,
        "max_turns": 4
    }
    session_response = client.post("/v1/sessions", json=session_request)
    assert session_response.status_code == 201
    session_id = session_response.json()["id"]

    turns_response = client.get(f"/v1/sessions/{session_id}/turns")
    assert turns_response.status_code == 200
    turns = turns_response.json()
    assert len(turns["items"]) == 4
    assert turns["items"][0]["role"] == "Keeper"

    feedback_response = client.get(f"/v1/sessions/{session_id}/feedback")
    assert feedback_response.status_code == 200
    feedback = feedback_response.json()
    assert set(feedback["metrics"].keys()) == {
        "pacing",
        "branching",
        "difficulty",
        "fairness",
        "cohesion",
        "tone"
    }


def test_roll_endpoint(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    sequence = iter([6, 2])

    def fake_randint(a: int, b: int) -> int:
        return next(sequence)

    monkeypatch.setattr("app.utils.dice.randint", fake_randint)

    response = client.post(
        "/v1/rolls",
        json={"expr": "1d100", "bonus": 0, "skill": 60}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["expr"] == "1d100"
    assert data["total"] == 26
    assert data["result"] in {"Success", "Hard", "Extreme", "Fail"}
    assert data["thresholds"] == {
        "regular": 60,
        "hard": 30,
        "extreme": 12
    }


def test_scenario_upload_and_query(client: TestClient) -> None:
    scenario_payload = {
        "name": "Haunted Manor",
        "content": (
            "探索者たちは古い洋館に足を踏み入れた。\n\n"
            "地下室には禁断の儀式の痕跡が残っている。\n\n"
            "屋根裏部屋には古文書が散乱していた。"
        ),
        "source_type": "md",
        "chunk_size": 300
    }

    create_response = client.post("/v1/scenarios", json=scenario_payload)
    assert create_response.status_code == 201
    scenario = create_response.json()
    scenario_id = scenario["id"]
    assert scenario["name"] == "Haunted Manor"
    assert len(scenario["chunks"]) >= 1
    assert scenario["chunks"][0]["content"].startswith("探索者たちは")

    list_response = client.get("/v1/scenarios")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/v1/scenarios/{scenario_id}")
    assert get_response.status_code == 200

    query_payload = {"query": "地下室", "top_k": 2}
    query_response = client.post(f"/v1/scenarios/{scenario_id}/query", json=query_payload)
    assert query_response.status_code == 200
    matches = query_response.json()["matches"]
    assert matches
    assert any("地下室" in match["content"] for match in matches)


def test_scenario_upload_endpoint(client: TestClient) -> None:
    files = {
        "file": ("note.txt", "探索者のメモ\n\n館の奥に不穏な気配がある".encode("utf-8"), "text/plain")
    }
    response = client.post("/v1/scenarios/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "note.txt"
    assert len(data["chunks"]) >= 1
