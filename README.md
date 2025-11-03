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

- Firebase Auth を有効化する場合は以下の変数を設定してください。
  - `FIREBASE_AUTH_DISABLED=0`
  - `FIREBASE_PROJECT_ID=<your-project-id>`
  - `FIREBASE_CREDENTIALS_PATH=<path-to-service-account.json>`（もしくは Application Default Credentials を使用）
  - 開発・テスト用途では `FIREBASE_AUTH_DISABLED=1` として認証をバイパス可能です。
  - フロントエンド側では Firebase Web SDK 用に以下の公開環境変数を設定します:
    - `NEXT_PUBLIC_FIREBASE_API_KEY`
    - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
    - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
    - `NEXT_PUBLIC_FIREBASE_APP_ID`

## Testing

- Backend: `uv run --extra dev pytest`
- Frontend lint: `npm run lint`
- Frontend tests: `npm run test`

## Docker

```bash
# Backend (FastAPI)
docker build -f infra/docker/api.Dockerfile -t trpg-evaluator-api .
docker run --env-file .env -p 8080:8080 trpg-evaluator-api

# Frontend (Next.js)
docker build -f infra/docker/web.Dockerfile -t trpg-evaluator-web .
docker run -p 3000:3000 trpg-evaluator-web
```

When running both containers together, serve them behind the same origin (e.g. via `docker compose` or a reverse proxy) so that the web app can reach `/v1/*` routes exposed by the API container.

## Deployment notes

The MVP targets Cloud Run for both services (see `SPEC.md` for release plan). Update `.tool-params/env.json` and `infra/` manifests before promoting to staging/production.

### Cloud Build promotion (staging → production)

A shared Cloud Build pipeline (`infra/gcp/cloudbuild.yaml`) builds both Docker images and deploys them to Cloud Run. Run it with environment-specific substitutions:

```bash
# Staging
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions _ENV=staging,_API_SERVICE=trpg-api-stg,_WEB_SERVICE=trpg-web-stg,_ARTIFACT_REPO=trpg-evaluator,_FIREBASE_API_KEY=<apiKey>,_FIREBASE_AUTH_DOMAIN=<authDomain>,_FIREBASE_PROJECT_ID=<projectId>,_FIREBASE_APP_ID=<appId>,_CORS_ALLOW_ORIGINS=https://trpg-web-stg-<project-number>.asia-northeast1.run.app

# Production
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions _ENV=prod,_API_SERVICE=trpg-api,_WEB_SERVICE=trpg-web,_ARTIFACT_REPO=trpg-evaluator,_FIREBASE_API_KEY=<apiKey>,_FIREBASE_AUTH_DOMAIN=<authDomain>,_FIREBASE_PROJECT_ID=<projectId>,_FIREBASE_APP_ID=<appId>,_CORS_ALLOW_ORIGINS=https://trpg-web-<project-number>.asia-northeast1.run.app
```

Set up Cloud Build triggers so that merges to `main` deploy to staging by default. After staging validation, rerun the build with `_ENV=prod` (manual approval or dedicated trigger) to promote the same images to production.
