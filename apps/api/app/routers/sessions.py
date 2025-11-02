from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.session import SessionCreateRequest, SessionFeedback, SessionResponse, TurnsResponse
from app.services import sessions

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(request: SessionCreateRequest):
    return sessions.create_session(request)


@router.get("/{session_id}/turns", response_model=TurnsResponse)
def get_turns(session_id: str, cursor: Optional[int] = Query(default=None, ge=0)):
    response = sessions.get_turns(session_id, cursor)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return response


@router.get("/{session_id}/feedback", response_model=SessionFeedback)
def get_feedback(session_id: str):
    response = sessions.get_feedback(session_id)
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return response


@router.get("/{session_id}/insights")
def get_insights(session_id: str):
    insights = sessions.get_insights(session_id)
    if insights is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return insights
