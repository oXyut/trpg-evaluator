from __future__ import annotations

import json
import logging
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Any, Dict, Optional


REQUEST_ID_VAR: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """Outputs log records as JSON with request correlation metadata."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = get_request_id()
        if request_id:
            payload["request_id"] = request_id

        structured = getattr(record, "structured", None)
        if isinstance(structured, dict):
            payload.update(structured)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)


def set_request_id(request_id: str) -> Token:
    return REQUEST_ID_VAR.set(request_id)


def get_request_id() -> Optional[str]:
    return REQUEST_ID_VAR.get()


def reset_request_id(token: Token) -> None:
    REQUEST_ID_VAR.reset(token)


def log_event(event: str, *, level: int = logging.INFO, **fields: Any) -> None:
    logger = logging.getLogger("trpg_evaluator")
    payload = {"event": event}
    payload.update(fields)
    logger.log(level, event, extra={"structured": payload})
