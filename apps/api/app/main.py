from __future__ import annotations

from fastapi import FastAPI

from app.routers import characters, evaluation, personalities, rolls, scenarios, sessions

app = FastAPI(title="TRPG Evaluator API", version="0.1.0")

app.include_router(characters.router)
app.include_router(personalities.router)
app.include_router(sessions.router)
app.include_router(rolls.router)
app.include_router(evaluation.router)
app.include_router(scenarios.router)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
