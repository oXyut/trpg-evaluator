# Dockerization Plan

This directory houses Dockerfiles for the web (Next.js) and api (FastAPI) services. Final images target Cloud Run deployment as described in `SPEC.md`.

- `api.Dockerfile`: Installs the FastAPI app and exposes `uvicorn` on port 8080.
- `web.Dockerfile`: Builds the Next.js dashboard and serves it with `next start` on port 3000.

Example commands (run from the repository root):

```bash
docker build -f infra/docker/api.Dockerfile -t trpg-evaluator-api .
docker build -f infra/docker/web.Dockerfile -t trpg-evaluator-web .
```
