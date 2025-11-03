import logging

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.scenario import ScenarioChunk, ScenarioModel
from app.services import rag


def _structured_entries(caplog):
    return [
        getattr(record, "structured")
        for record in caplog.records
        if isinstance(getattr(record, "structured", None), dict)
    ]


def test_request_logging_uses_provided_request_id(caplog):
    client = TestClient(app)
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="trpg_evaluator"):
        response = client.get("/healthz", headers={"x-request-id": "req-test-123"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-test-123"

    entries = _structured_entries(caplog)
    tracked = [entry for entry in entries if entry.get("event") in {"http.request.start", "http.request.complete"}]
    assert tracked, "ログにHTTPイベントが出力されていません"
    for entry in tracked:
        assert entry["request_id"] == "req-test-123"


def test_rag_retrieve_emits_structured_log(caplog):
    scenario = ScenarioModel(
        id="scn_1",
        name="Test",
        source_type="md",
        content="dummy",
        chunks=[
            ScenarioChunk(id="chunk-1", order=0, content="地下室には儀式の痕跡が残っている。"),
            ScenarioChunk(id="chunk-2", order=1, content="屋根裏には古文書が散乱している。"),
        ],
    )

    caplog.clear()
    with caplog.at_level(logging.INFO, logger="trpg_evaluator"):
        matches = rag.simple_retrieve("地下室", scenario, top_k=2)

    assert matches, "RAG結果が返却されていません"
    entries = _structured_entries(caplog)
    rag_logs = [entry for entry in entries if entry.get("event") == "rag.retrieve"]
    assert rag_logs, "RAGのログが出力されていません"
    last_entry = rag_logs[-1]
    assert last_entry["scenario_id"] == "scn_1"
    assert last_entry["match_count"] == len(matches)
    assert "elapsed_ms" in last_entry
