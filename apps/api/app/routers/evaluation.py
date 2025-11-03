from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.session import SessionFeedback
from app.services import sessions

router = APIRouter(prefix="/v1/evaluation", tags=["evaluation"])


@router.get("/{session_id}", response_model=SessionFeedback)
def get_evaluation(session_id: str):
    feedback = sessions.get_feedback(session_id)
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return feedback
