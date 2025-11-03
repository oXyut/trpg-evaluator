from __future__ import annotations

import logging
import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.utils.logging import (
    configure_logging,
    log_event,
    reset_request_id,
    set_request_id,
)
from app.utils.auth import FirebaseAuthError, FirebaseUser, is_auth_disabled, verify_firebase_token

from app.routers import characters, evaluation, personalities, rolls, scenarios, sessions

configure_logging()

app = FastAPI(title="TRPG Evaluator API", version="0.1.0")

allowed_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if allowed_origins_env:
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    allowed_origins = ["*"] if os.getenv("CORS_ALLOW_ALL", "0").lower() in {"1", "true", "yes"} else []

if allowed_origins:
    log_event("cors.configuration", origins=allowed_origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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


def _requires_auth(path: str) -> bool:
    if is_auth_disabled():
        return False
    if path == "/healthz":
        return False
    return path.startswith("/v1/")


@app.middleware("http")
async def firebase_auth_middleware(request: Request, call_next):
    if _requires_auth(request.url.path):
        header = request.headers.get("authorization")
        if not header or not header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing bearer token"},
            )
        token = header.split(" ", 1)[1].strip()
        try:
            user = verify_firebase_token(token)
            log_event("auth.token.verified", uid=user.uid, email=user.email)
        except FirebaseAuthError as exc:
            log_event("auth.token.invalid", level=logging.WARNING, error=str(exc))
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Firebase token"},
            )
        request.state.user = user
    else:
        request.state.user = FirebaseUser(uid="anonymous")
    return await call_next(request)


def get_current_user(request: Request) -> FirebaseUser:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
