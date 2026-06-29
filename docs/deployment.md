# Deployment Guide

This project deploys as a modular monolith with separate web services for the
FastAPI backend and the frontend. PostgreSQL is provided by Neon.

## Production Targets

- Backend: Render web service using `Dockerfile.backend`.
- Frontend: Render web service using `Dockerfile.frontend`, running the Next.js
  production server.
- Database: Neon PostgreSQL.
- CI: GitHub Actions in `.github/workflows/ci.yml`.

## Render Blueprint

The repository includes `render.yaml` for both web services.

### Backend

Render runs:

- Build: Docker image from `Dockerfile.backend`.
- Pre-deploy: `python -m alembic upgrade head`.
- Start: the Docker `CMD`, which runs Uvicorn on Render's injected `PORT`.
- Health check: `GET /health`.

Required Render environment variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `FRONTEND_BASE_URL`
- `BACKEND_BASE_URL`
- `ALLOWED_ORIGINS`
- `ADMIN_EMAILS`
- `TOURNAMENT_PROVIDER_BASE_URL`
- `TOURNAMENT_PROVIDER_API_KEY` if the configured provider requires it
- `TOURNAMENT_PROVIDER_TIMEOUT_SECONDS`

Use Render secret/synced environment values for every secret. Do not commit
production values to the repository.

### Frontend

Render runs:

- Build: Docker image from `Dockerfile.frontend`.
- Start: the Docker `CMD`, which runs the Next.js standalone server on Render's
  injected `PORT`.
- Health check: `GET /health`.

Required Render environment variables:

- `NEXT_PUBLIC_API_BASE_URL`: browser-visible public backend URL, for example
  `https://worldcup-pool-api.onrender.com`.
- `API_BASE_URL`: server-side backend URL. In production this can match
  `NEXT_PUBLIC_API_BASE_URL`; in Docker Compose it points at `http://backend:8000`.
- `FRONTEND_BASE_URL`: public frontend URL, for example
  `https://worldcup-pool-frontend.onrender.com`.

The backend `FRONTEND_BASE_URL` and `ALLOWED_ORIGINS` values must match the
frontend public URL.

### Scheduled Fixture Sync

`render.yaml` also defines `worldcup-pool-fixture-sync`, a Render cron job that
uses the backend Docker image and runs:

```sh
python -m scripts.sync_knockout_fixtures "$TOURNAMENT_SYNC_TOURNAMENT_ID" --year "${TOURNAMENT_SYNC_YEAR:-2026}" --mode "${TOURNAMENT_SYNC_MODE:-all}"
```

The job is scheduled every 15 minutes. This is intentionally frequent enough
for match-day kickoff/result updates while still being simple to reason about.
Before enabling production sync, configure these Render variables on the cron
job:

- `DATABASE_URL`: same Neon database URL as the backend.
- `TOURNAMENT_SYNC_TOURNAMENT_ID`: internal tournament UUID.
- `TOURNAMENT_SYNC_YEAR`: normally `2026`.
- `TOURNAMENT_SYNC_MODE`: normally `all`; use `results` for result-only retry.
- `TOURNAMENT_PROVIDER_BASE_URL`: provider or self-hosted adapter base URL.
- `TOURNAMENT_PROVIDER_API_KEY`: secret provider key when required.
- `TOURNAMENT_PROVIDER_TIMEOUT_SECONDS`: request timeout, default `10`.

The cron job prints a one-line summary with created/updated counts and prints
individual errors without provider payloads or secrets. Failed provider calls
return non-zero from the script and do not corrupt existing data.

## Neon

Create a Neon PostgreSQL project and copy its connection string into Render as
`DATABASE_URL`.

The application accepts either of these URL forms:

- `postgresql://...`
- `postgresql+psycopg://...`

At runtime, settings normalize `postgresql://` into the SQLAlchemy psycopg
driver format.

## Google OAuth

Create a Google OAuth client of type `Web application`.

Authorized redirect URI for production:

```text
https://<backend-render-host>/api/v1/auth/google/callback
```

Then configure:

- `GOOGLE_REDIRECT_URI` with the same backend callback URL.
- `BACKEND_BASE_URL` with the public backend URL.
- `FRONTEND_BASE_URL` with the public frontend URL.
- `ALLOWED_ORIGINS` with the public frontend URL.

The redirect URI must match exactly in Google Cloud Console and Render.
When `ENVIRONMENT=production`, backend startup requires these values to be set
explicitly and rejects localhost URLs.

## Local Docker

Start the stack:

```powershell
docker compose up --build
```

The `migrate` Compose service runs Alembic before the backend starts.

Seed development data:

```powershell
docker compose exec backend python -m scripts.seed_dev_data
```

Run a local fixture sync against the Docker database:

```powershell
$env:TOURNAMENT_SYNC_TOURNAMENT_ID = "<local-tournament-uuid>"
docker compose --profile tools run --rm fixture-sync
```

For result-only retry:

```powershell
$env:TOURNAMENT_SYNC_MODE = "results"
docker compose --profile tools run --rm fixture-sync
```

Open:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Backend health check: `http://localhost:8000/health`
- Frontend health check: `http://localhost:3000/health`

## Release Checklist

1. GitHub Actions passes.
2. Render environment variables are configured.
3. Neon database is reachable from Render.
4. `API_BASE_URL`, `FRONTEND_BASE_URL`, and `ALLOWED_ORIGINS` use deployed
   HTTPS URLs.
5. Google OAuth redirect URI matches the deployed backend callback.
6. Render pre-deploy migration succeeds.
7. `worldcup-pool-fixture-sync` has `TOURNAMENT_SYNC_TOURNAMENT_ID` and provider
   variables configured, or the cron job is intentionally paused until the
   tournament record exists.
8. Backend `/health` returns `{"status": "ok", "database": "ok"}`.
9. Frontend `/health` returns a 2xx status.
10. Manual fixture sync dry run succeeds before relying on the schedule.

## Fixture Sync Runbook

### Normal Operation

1. Confirm BE-005 migrations have run.
2. Set the provider and tournament sync environment variables in Render.
3. Trigger a manual cron run in Render or run the command once from a shell.
4. Confirm the summary shows expected created/updated counts.
5. Check backend match responses for `provider_last_synced_at`, `sync_source`,
   and `admin_override`.

### Provider Failure

1. Inspect the cron run logs for the printed error summary.
2. Confirm no secrets or raw provider credentials are present in logs.
3. Retry with `TOURNAMENT_SYNC_MODE=results` if fixture/team import is already
   healthy and only result sync failed.
4. Use admin match completion or kickoff correction as fallback when provider
   data is unavailable or wrong.

### Rollback and Recovery

1. Pause the Render cron job if repeated provider failures or bad data appear.
2. Correct affected matches through admin endpoints. Manual corrections set
   `admin_override=true`, so later provider runs do not silently overwrite them.
3. Re-run `POST /api/v1/admin/matches/{match_id}/rescore` for completed matches
   after a correction when needed.
4. Resume the cron job only after provider data and environment variables are
   verified.
