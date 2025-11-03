from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request, Response

from app.utils.logging import (
    configure_logging,
    log_event,
    reset_request_id,
    set_request_id,
)

from app.routers import characters, evaluation, personalities, rolls, scenarios, sessions

configure_logging()

app = FastAPI(title="TRPG Evaluator API", version="0.1.0")

app.include_router(characters.router)
app.include_router(personalities.router)
app.include_router(sessions.router)
app.include_router(rolls.router)
app.include_router(evaluation.router)
app.include_router(scenarios.router)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    incoming = request.headers.get("x-request-id")
    request_id = incoming or str(uuid.uuid4())
    token = set_request_id(request_id)
    started = time.perf_counter()
    log_event(
        "http.request.start",
        method=request.method,
        path=str(request.url.path),
        client=request.client.host if request.client else None,
    )
    try:
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        log_event(
            "http.request.complete",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            elapsed_ms=duration_ms,
        )
        return response
    except Exception as exc:  # pragma: no cover - propagated for FastAPI handlers
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(
            "http.request.error",
            level=logging.ERROR,
            method=request.method,
            path=str(request.url.path),
            error=str(exc),
            elapsed_ms=duration_ms,
        )
        raise
    finally:
        reset_request_id(token)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
