# Infrastructure

## Overview

The infrastructure is intentionally simple for the MVP:

- One FastAPI backend service.
- One frontend service.
- One managed PostgreSQL database.
- One scheduled fixture sync cron job during tournament operations.
- CI checks in GitHub Actions.
- Docker images as the deployment unit.

This keeps the architecture cloud-ready without introducing microservices or
unnecessary runtime components.

## Services

### Backend

- Platform: Render.
- Runtime: Docker.
- Image: `Dockerfile.backend`.
- ASGI app: `app.api.main:app`.
- Health endpoint: `/health`.
- Database migrations: Alembic through Render `preDeployCommand`.

### Frontend

- Platform: Render.
- Image: `Dockerfile.frontend`.
- Runtime: Next.js standalone server.
- Health endpoint: `/health`.
- API access: HTTP calls to the backend REST API only.

### Database

- Platform: Neon PostgreSQL.
- Access: `DATABASE_URL`.
- Schema changes: Alembic migrations only.
- Local development: PostgreSQL service in `docker-compose.yml`.

### Fixture Sync Cron

- Platform: Render cron job.
- Image: `Dockerfile.backend`.
- Command: `python -m scripts.sync_knockout_fixtures`.
- Schedule: every 15 minutes in production while tournament data operations are
  active.
- Configuration: provider base URL/key/timeout plus
  `TOURNAMENT_SYNC_TOURNAMENT_ID`.
- Safety: sync operations are idempotent and skip provider writes for matches
  with `admin_override=true`.

## Docker

`Dockerfile.backend` builds the production backend image. It installs the
project package and starts Uvicorn with the injected `PORT`.

`Dockerfile.frontend` builds the Next.js app with `npm ci` and runs the
standalone production server with Render's injected `PORT`.

`docker-compose.yml` is for local development and includes:

- `db`
- `migrate`
- `backend`
- `frontend`
- optional `fixture-sync` profile service for manual local sync runs
- `postgres_data` volume

The `migrate` service runs Alembic after PostgreSQL is healthy and before the
backend starts.

The `fixture-sync` service is not part of the default `docker compose up` path.
Run it explicitly with `docker compose --profile tools run --rm fixture-sync`
after setting `TOURNAMENT_SYNC_TOURNAMENT_ID`.

## CI

The GitHub Actions workflow runs on pushes to `main` and pull requests.

Checks:

- Python dependency installation.
- Ruff linting.
- Python compilation.
- Backend test suite, including migration smoke and repository integration tests
  against a PostgreSQL service database.
- Frontend test suite.
- Docker Compose configuration validation.
- Backend Docker image build.
- Frontend Docker image build.

The backend CI job provisions PostgreSQL 16 with a disposable non-secret
`DATABASE_URL`/`TEST_DATABASE_URL` and `ENVIRONMENT=test`. Integration tests
continue to skip safely outside CI when no safe local or explicit test database
is configured.

Render is configured with `autoDeployTrigger: checksPass`, so services deploy
from the linked branch only after GitHub checks pass.

`render.yaml` defines the scheduled sync as a cron service. Render's Blueprint
reference supports `type: cron`, a cron-expression `schedule`, and
`dockerCommand` for Docker-based services. The cron service should be paused or
left without production variables until the production tournament UUID exists.

## Operational Notes

- Keep `ENVIRONMENT=production` in Render.
- Use Render secret values for credentials.
- Configure `GOOGLE_REDIRECT_URI` to the backend callback URL:
  `https://<backend-host>/api/v1/auth/google/callback`.
- Configure `FRONTEND_BASE_URL` and `ALLOWED_ORIGINS` to the public frontend
  origin, and `BACKEND_BASE_URL` to the public backend origin.
- Use Neon pooled or direct URLs according to the workload. Direct URLs are
  usually simpler for migrations.
- Keep migrations backward-compatible when possible.
- Check backend `/health` and frontend `/health` after each deploy.
- Check fixture sync cron logs for created/updated/error counts after each run.
- Use match `provider_last_synced_at`, `sync_source`, and `admin_override` fields
  as the MVP operational visibility surface.
- Pause the cron job before investigating repeated provider failures or bad
  upstream data.
