from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

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
