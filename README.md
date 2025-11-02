# TRPG Evaluator

MVP implementation for the Call of Cthulhu scenario evaluator described in `SPEC.md`. The repo follows a monorepo layout with FastAPI backend and Next.js frontend apps.

## Repository layout

- `apps/api`: FastAPI service exposing `/v1/characters`, `/v1/personalities`, `/v1/sessions`, `/v1/rolls`, `/v1/scenarios`。
- `apps/web`: Next.js 14 dashboard for uploading scenarios, browsing stored content, running keyword queries, and reviewing simulated session logs & feedback.
- `packages/schema`: Shared JSON schema definitions (e.g. `characters.json`) for cross-language validation.
- `packages/ui`: Placeholder for reusable UI components.
- `infra/`: Deployment scaffolding (Cloud Run & GCP docs).
- `.tool-params/env.json`: Deployment constants for Codex workflows.

## Prerequisites

- Node.js 18+
- Python 3.12+

## Backend (FastAPI)

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

### API smoke test

```bash
curl -X POST http://localhost:8000/v1/rolls \
  -H 'Content-Type: application/json' \
  -d '{"expr":"1d100","bonus":1,"skill":65}'
```

## Frontend (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

Visit `http://localhost:3000` to open the dashboard.

## Environment variables

Runtime configuration lives in `.env`. See the file for defaults covering API host/port and emulator hints.

## Testing

- Backend: `uv run --extra dev pytest`
- Frontend lint: `npm run lint`
- Frontend tests: `npm run test`

## Deployment notes

The MVP targets Cloud Run for both services (see `SPEC.md` for release plan). Update `.tool-params/env.json` and `infra/` manifests before promoting to staging/production.
