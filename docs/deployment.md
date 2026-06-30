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

The default `render.yaml` blueprint does not define a Render cron service. It
provisions only the backend and frontend web services so the free-plan path
cannot accidentally create an unsupported scheduled service.

For the current free-plan path, run the sync command from a trusted local or
operator-controlled machine against the Neon `DATABASE_URL` on a schedule:

```sh
python -m scripts.sync_knockout_fixtures "$TOURNAMENT_SYNC_TOURNAMENT_ID" --year "${TOURNAMENT_SYNC_YEAR:-2026}" --mode "${TOURNAMENT_SYNC_MODE:-all}"
```

Admin-triggered sync and manual corrections remain available in the app as
fallbacks.

Render cron is an optional convenience for a later paid/eligible Render plan.
When that path is intentionally adopted, add a separate Render cron service that
uses the backend Docker image, runs the command above, and schedules it every 15
minutes during tournament operations. Do not add that service to the default
free-plan blueprint.

Before enabling Render cron or a local scheduled sync, configure these
variables in the scheduler environment:

- `DATABASE_URL`: same Neon database URL as the backend.
- `TOURNAMENT_SYNC_TOURNAMENT_ID`: internal tournament UUID for the production
  tournament row.
- `TOURNAMENT_SYNC_YEAR`: normally `2026`.
- `TOURNAMENT_SYNC_MODE`: normally `all`; use `results` for result-only retry.
- `TOURNAMENT_PROVIDER_BASE_URL`: provider or self-hosted adapter base URL.
- `TOURNAMENT_PROVIDER_API_KEY`: secret provider key when required.
- `TOURNAMENT_PROVIDER_TIMEOUT_SECONDS`: request timeout, default `10`.

The sync job prints a one-line summary with created/updated counts and prints
individual errors without provider payloads or secrets. Failed provider calls
return non-zero from the script and do not corrupt existing data.

### Free-Plan Local Scheduled Sync

When Render cron is not enabled, schedule the sync locally against Neon from a
trusted machine that can store environment variables securely.

Prerequisites:

1. Backend migrations have run against Neon.
2. The production tournament row exists.
3. The operator has the internal tournament UUID. Get it from the database, an
   authenticated admin/API response, or another trusted operational record; do
   not use a pool UUID or provider external ID.
4. The scheduler environment has the Neon `DATABASE_URL`, provider variables,
   and `TOURNAMENT_SYNC_TOURNAMENT_ID`.
5. A Python virtual environment exists on the operator machine with project
   dependencies installed, or the operator uses the backend Docker image.

One-time PowerShell smoke run from the repository root:

```powershell
$env:DATABASE_URL = "<neon-postgresql-url>"
$env:TOURNAMENT_SYNC_TOURNAMENT_ID = "<production-tournament-uuid>"
$env:TOURNAMENT_SYNC_YEAR = "2026"
$env:TOURNAMENT_SYNC_MODE = "all"
$env:TOURNAMENT_PROVIDER_BASE_URL = "<provider-or-self-hosted-base-url>"
$env:TOURNAMENT_PROVIDER_API_KEY = "<provider-key-if-required>"
$env:TOURNAMENT_PROVIDER_TIMEOUT_SECONDS = "10"
.\.venv\Scripts\python.exe -m scripts.sync_knockout_fixtures $env:TOURNAMENT_SYNC_TOURNAMENT_ID --year $env:TOURNAMENT_SYNC_YEAR --mode $env:TOURNAMENT_SYNC_MODE
```

Do not paste production values into `.env.example`, documentation, shell
history that is shared, screenshots, issue comments, or commits. Prefer a
dedicated operator account, Windows Credential Manager, a password manager, or
the scheduler's protected secret storage for real values.

Windows Task Scheduler example action:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "cd C:\dev\worldcup-pool-app; .\.venv\Scripts\python.exe -m scripts.sync_knockout_fixtures $env:TOURNAMENT_SYNC_TOURNAMENT_ID --year $env:TOURNAMENT_SYNC_YEAR --mode $env:TOURNAMENT_SYNC_MODE"
```

Windows Task Scheduler setup:

1. Create a task named `WorldCup Pool Fixture Sync`.
2. Run whether the operator is logged on or not.
3. Use a dedicated operator account with access only to this repository and the
   required secrets.
4. Trigger every 15 minutes during tournament operations.
5. Set the action to `powershell.exe`.
6. Set arguments to the example command above, adjusting the repository and
   Python paths for the operator machine.
7. Store required environment variables at the machine/user level or in a
   protected wrapper managed by the operator. Do not store real secrets in the
   repository.
8. Enable task history and redirect output to an operator-controlled log path if
   needed, for example by wrapping the command in a local script outside the
   repository.

Linux/macOS equivalent:

```sh
cd /srv/worldcup-pool-app
TOURNAMENT_SYNC_TOURNAMENT_ID="$TOURNAMENT_SYNC_TOURNAMENT_ID" \
  ./.venv/bin/python -m scripts.sync_knockout_fixtures \
  "$TOURNAMENT_SYNC_TOURNAMENT_ID" \
  --year "${TOURNAMENT_SYNC_YEAR:-2026}" \
  --mode "${TOURNAMENT_SYNC_MODE:-all}"
```

Required local scheduler variables:

- `DATABASE_URL`: Neon database URL.
- `TOURNAMENT_SYNC_TOURNAMENT_ID`: internal tournament UUID.
- `TOURNAMENT_SYNC_YEAR`: normally `2026`.
- `TOURNAMENT_SYNC_MODE`: normally `all`.
- `TOURNAMENT_PROVIDER_BASE_URL`.
- `TOURNAMENT_PROVIDER_API_KEY` if required by the provider.
- `TOURNAMENT_PROVIDER_TIMEOUT_SECONDS`.

Store these variables in the scheduler or operator environment, not in the
repository. The trade-off is operational: the local machine must be online and
monitored during tournament operations. If that is not acceptable, enable
Render cron or another managed scheduler before the tournament.

Expected logs:

- Successful runs print one summary line:
  `teams_created=... teams_updated=... matches_created=... matches_updated=... errors=0`.
- Failed runs print the summary plus `error: ...` lines and exit non-zero.
- Logs must not include database URLs, OAuth secrets, provider keys, or raw
  provider payloads.

Retry and disable guidance:

- For transient provider failures, rerun the task once after checking logs.
- If teams and fixture import are healthy but result sync failed, retry with
  `TOURNAMENT_SYNC_MODE=results`.
- Disable or pause the scheduled task before investigating repeated failures,
  bad upstream data, or suspected secret exposure.
- Use admin sync/manual correction endpoints while the scheduler is paused.
- Rotate any secret that may have been pasted into logs, screenshots, chat, or a
  committed file.

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
7. Scheduled sync has `TOURNAMENT_SYNC_TOURNAMENT_ID` and provider variables
   configured in the local/operator scheduler for the free-plan path, or in
   Render cron only when that optional plan-dependent service is enabled.
   Otherwise sync is intentionally paused until the tournament record exists.
8. Backend `/health` returns `{"status": "ok", "database": "ok"}`.
9. Frontend `/health` returns a 2xx status.
10. Manual fixture sync dry run succeeds before relying on the schedule.

## Fixture Sync Runbook

### Normal Operation

1. Confirm BE-005 migrations have run.
2. Confirm the production tournament UUID and set
   `TOURNAMENT_SYNC_TOURNAMENT_ID` to that internal UUID.
3. Set the provider and tournament sync environment variables in the active
   scheduler environment: Render cron if enabled, otherwise the local/operator
   scheduler.
4. Trigger a manual scheduler run or run the command once from a shell.
5. Confirm the summary shows expected created/updated counts.
6. Check backend match responses for `provider_last_synced_at`, `sync_source`,
   and `admin_override`.

### Provider Failure

1. Inspect the scheduler logs for the printed error summary.
2. Confirm no secrets or raw provider credentials are present in logs.
3. Retry with `TOURNAMENT_SYNC_MODE=results` if fixture/team import is already
   healthy and only result sync failed.
4. Use admin match completion or kickoff correction as fallback when provider
   data is unavailable or wrong.

### Rollback and Recovery

1. Pause the active scheduler if repeated provider failures or bad data appear.
2. Correct affected matches through admin endpoints. Manual corrections set
   `admin_override=true`, so later provider runs do not silently overwrite them.
3. Re-run `POST /api/v1/admin/matches/{match_id}/rescore` for completed matches
   after a correction when needed.
4. Resume scheduled sync only after provider data and environment variables are
   verified.
