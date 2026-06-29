# Infrastructure

## Overview

The infrastructure is intentionally simple for the MVP:

- One FastAPI backend service.
- One frontend service.
- One managed PostgreSQL database.
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
- `postgres_data` volume

The `migrate` service runs Alembic after PostgreSQL is healthy and before the
backend starts.

## CI

The GitHub Actions workflow runs on pushes to `main` and pull requests.

Checks:

- Python dependency installation.
- Ruff linting.
- Python compilation.
- Backend and frontend test suites.
- Docker Compose configuration validation.
- Backend Docker image build.
- Frontend Docker image build.

Render is configured with `autoDeployTrigger: checksPass`, so services deploy
from the linked branch only after GitHub checks pass.

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
