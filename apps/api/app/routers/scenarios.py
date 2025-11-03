from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.schemas.scenario import (
    ScenarioCreateRequest,
    ScenarioQueryRequest,
    ScenarioQueryResponse,
    ScenarioResponse,
)
from app.services import scenarios

router = APIRouter(prefix="/v1/scenarios", tags=["scenarios"])


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(request: ScenarioCreateRequest):
    return scenarios.create_scenario(request)


@router.post("/upload", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def upload_scenario(file: UploadFile):
    filename = file.filename or "uploaded_scenario.txt"
    if not filename.lower().endswith(('.md', '.txt')) and not file.content_type.startswith("text/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only text/markdown uploads supported in MVP")

    try:
        payload = await file.read()
        content = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to decode file as UTF-8 text") from exc

    if not content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    scenarios.persist_raw_upload(filename, content)
    return scenarios.create_scenario_from_text(name=filename, content=content)


@router.get("", response_model=list[ScenarioResponse])
def list_scenarios():
    return scenarios.list_scenarios()


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: str):
    response = scenarios.get_scenario(scenario_id)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return response


@router.post("/{scenario_id}/query", response_model=ScenarioQueryResponse)
def query_scenario(scenario_id: str, request: ScenarioQueryRequest):
    response = scenarios.query_scenario(scenario_id, request)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return response
