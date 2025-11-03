# GCP Infrastructure

## Overview

Production and staging deployments are handled via Cloud Build pipelines that build the docker images and deploy them to Cloud Run. The shared pipeline definition lives in `cloudbuild.yaml` and relies on substitution parameters to toggle between staging / production.

```
infra/gcp/
  cloudbuild.yaml   # Cloud Build pipeline for API + Web deployment
```

## Prerequisites

1. Enable APIs in the GCP project:
   - Cloud Build API
   - Artifact Registry API
   - Cloud Run Admin API
2. Create an Artifact Registry repository (e.g. `trpg-evaluator`) in the target region (default `asia-northeast1`).
3. Provision two Cloud Run services each for staging and production, or allow the pipeline to create them automatically on first deploy.
4. Grant the Cloud Build service account the following roles:
   - Artifact Registry Writer
   - Cloud Run Admin
   - Service Account User (for the runtime service account of the deployed services)

## Running the pipeline manually

Staging deploy:

```bash
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions _ENV=staging,_API_SERVICE=trpg-api-stg,_WEB_SERVICE=trpg-web-stg,_ARTIFACT_REPO=trpg-evaluator
```

Production deploy:

```bash
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions _ENV=prod,_API_SERVICE=trpg-api,_WEB_SERVICE=trpg-web,_ARTIFACT_REPO=trpg-evaluator
```

The pipeline will:

1. Build and push Docker images for API / Web to Artifact Registry.
2. Deploy the images to Cloud Run with environment specific tags (`${_ENV}-${SHORT_SHA}`).
3. Set environment variables so the Web app points at the correct API host.

## Recommended promotion flow

1. Merge to the main branch triggers the staging Cloud Build (configure via Cloud Build trigger or GitHub Actions → Cloud Build). `_ENV=staging` with staging service names.
2. After validating staging, promote to production by re-running the build with `_ENV=prod` substitutions (can be automated via approval-based Cloud Build trigger).

Document the Cloud Build trigger IDs and service names in your team runbook so future deployments can reuse the parameters.
