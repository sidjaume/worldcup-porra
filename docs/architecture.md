# Architecture

## Purpose

This application is a private FIFA World Cup 2026 knockout prediction pool. It manages only the completed-tournament knockout bracket:

- Round of 32
- Round of 16
- Quarter-finals
- Semi-finals
- Final

The application does not model group stage standings, group predictions, qualification rules, or team qualification calculations.

## System Architecture

The MVP uses a modular monolith split into two deployable processes:

- Backend: FastAPI REST API, domain services, repositories, migrations, and authentication.
- Frontend: Streamlit app that renders the user experience and talks to the backend through HTTP APIs.
- Database: Neon PostgreSQL, accessed only by backend repositories.

```text
Browser
  |
  v
Render Web Service: Streamlit frontend
  |
  | HTTPS REST calls with bearer token
  v
Render Web Service: FastAPI backend
  |
  | SQLAlchemy repositories
  v
Neon PostgreSQL

Google OAuth 2.0
  ^
  |
FastAPI backend owns OAuth redirects, callback handling, user provisioning,
and application token issuance.
```

## Architectural Principles

- Keep business rules independent from FastAPI, Streamlit, PostgreSQL, and Google OAuth.
- Treat the domain layer as the source of truth for scoring, prediction locks, and knockout progression rules.
- Use repositories for all database access.
- Keep Streamlit pages thin: UI state, forms, rendering, and API client calls only.
- Use migrations for every database schema change.
- Prefer explicit, simple service classes over broad abstractions.
- Design for 10-100 users per pool first, while avoiding choices that block later growth.

## Backend Module Structure

Recommended initial structure:

```text
app/
  api/
    main.py
    dependencies.py
    errors.py
    middleware.py
    routers/
      auth.py
      users.py
      pools.py
      participants.py
      tournaments.py
      matches.py
      predictions.py
      rankings.py
    schemas/
      auth.py
      users.py
      pools.py
      tournaments.py
      matches.py
      predictions.py
      rankings.py
  config/
    settings.py
    logging.py
  domain/
    entities/
      scoring.py
      prediction.py
      bracket.py
    enums.py
    errors.py
    services/
      scoring_engine.py
      prediction_policy.py
      bracket_progression.py
  services/
    auth_service.py
    user_service.py
    pool_service.py
    tournament_service.py
    prediction_service.py
    ranking_service.py
  repositories/
    base.py
    users.py
    oauth_accounts.py
    pools.py
    participants.py
    teams.py
    matches.py
    predictions.py
    scores.py
  models/
    base.py
    user.py
    pool.py
    participant.py
    tournament.py
    team.py
    match.py
    prediction.py
    score.py
  db/
    session.py
    migrations/
  tests/
    domain/
    services/
    api/
    repositories/
```

### Backend Responsibilities

`api`
: FastAPI application setup, request/response schemas, routers, dependencies, middleware, and exception mapping.

`domain`
: Pure Python rules for scoring, prediction lock checks, match outcome interpretation, and bracket advancement. This layer must not import FastAPI, SQLAlchemy, Streamlit, Google clients, or settings.

`services`
: Application use cases. Services coordinate repositories, domain rules, authorization checks, and transaction boundaries.

`repositories`
: SQL persistence. Repositories should expose intent-focused methods rather than leaking query details into services.

`models`
: SQLAlchemy ORM models that map to PostgreSQL tables.

`config`
: Environment-based settings, logging, CORS, token configuration, and external provider configuration.

## Domain Boundaries

### Scoring

The scoring engine accepts plain input values:

- Predicted home goals
- Predicted away goals
- Actual home goals
- Actual away goals
- Optional scoring configuration

It returns a result object with total points and reason codes:

- `correct_winner`
- `exact_score`
- `partial_home_goals`
- `partial_away_goals`

Default scoring:

- Correct winner: 2 points
- Exact score: 2 additional points
- One exact team goal count: 1 additional point per matching team goal count

Exact score implies both goal counts are correct, but the MVP rule awards only the exact-score bonus, not two partial bonuses on top of exact score. A Spain 3-1 prediction for an actual Spain 3-1 result is therefore 4 total points.

### Prediction Locking

Prediction editability is based on match `scheduled_at` and the match status. A prediction is writable only when:

- The match status is `scheduled`.
- The current server time is earlier than the match lock time.

The default lock time is match kickoff, represented by `matches.scheduled_at`. A future configuration can add a per-match or per-pool `lock_offset_minutes`.

### Knockout Progression

The bracket stores explicit match links:

- Each match can point to its next match.
- Each match defines whether the winner advances into the next match home or away slot.

When a completed match has a winner, the backend progression service writes the winner into the linked next match slot. This avoids calculating FIFA qualification rules and keeps the bracket editable by an admin.

## Frontend Structure

Recommended Streamlit structure:

```text
frontend/
  app.py
  api_client/
    client.py
    auth.py
    pools.py
    tournaments.py
    predictions.py
    rankings.py
  components/
    auth_status.py
    pool_selector.py
    match_card.py
    prediction_form.py
    ranking_table.py
    bracket_view.py
  pages/
    01_dashboard.py
    02_pools.py
    03_predictions.py
    04_rankings.py
    05_profile.py
  state/
    session.py
  config.py
```

### Frontend Responsibilities

- Render dashboard, pools, predictions, rankings, and profile screens.
- Store the current access token in Streamlit session state.
- Call backend APIs through a small typed API client.
- Show backend validation errors clearly.
- Avoid direct database access.
- Avoid scoring, locking, and bracket progression logic.

### Initial Screens

- Dashboard: active pools, next locked matches, recent points changes.
- Pools: create pool, join pool by invite code, participant list.
- Predictions: match list by round, prediction forms for unlocked matches, read-only state for locked/completed matches.
- Rankings: pool ranking table with points and prediction counts.
- Profile: user display name and account details.

## Security Model

- Backend validates every authenticated request with a signed application token.
- Backend authorizes pool access by checking pool membership.
- Invite codes are random, unique, and stored as hashes or non-guessable tokens.
- Google client secrets are used only by the backend.
- Secrets are configured through environment variables, never committed.
- CORS allows only configured frontend origins.
- Backend logs must avoid tokens, invite codes, OAuth payloads, and personal data beyond operational identifiers.

## Operational Requirements

- FastAPI exposes `/health` for Render health checks.
- Backend startup validates required settings.
- Database migrations are run through Alembic.
- Production uses a PostgreSQL connection string from Neon with SSL required.
- Docker images should run without local filesystem persistence.
- All timestamps are stored in UTC.

## Deployment Overview

- Render service 1: FastAPI backend web service.
- Render service 2: Streamlit frontend web service.
- Neon: managed PostgreSQL project.
- Google Cloud Console: OAuth client with backend callback URL and frontend redirect URL allowlists.

The backend start command should run a production ASGI server such as Uvicorn or Gunicorn with Uvicorn workers. Render provides a `$PORT` environment variable for web services, so both backend and frontend must bind to `0.0.0.0:$PORT`.

## Deployment Strategy: Render + Neon

### Render Services

Deploy two independent Render web services from the same repository:

```text
worldcup-pool-api
  runtime: Docker or Python
  process: FastAPI ASGI app
  health check path: /health
  start command example: uvicorn app.api.main:app --host 0.0.0.0 --port $PORT

worldcup-pool-web
  runtime: Docker or Python
  process: Streamlit app
  start command example: streamlit run frontend/app.py --server.address 0.0.0.0 --server.port $PORT
```

Use Docker for reproducible production builds once the project has dependencies and entrypoints. Native Render Python services are acceptable during early MVP development, but Docker should be the production target because it keeps local and cloud runtime behavior closer.

### Neon Database

Create one Neon project for production and use a PostgreSQL connection string exposed as `DATABASE_URL` to the backend. Neon connection strings should require SSL. Use separate Neon branches or separate projects for development/staging if collaborative testing needs isolated data.

The Streamlit service must not receive `DATABASE_URL`.

### Required Environment Variables

Backend:

```text
DATABASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
SECRET_KEY=
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
FRONTEND_BASE_URL=
BACKEND_BASE_URL=
ALLOWED_ORIGINS=
ENVIRONMENT=production
```

Frontend:

```text
API_BASE_URL=
FRONTEND_BASE_URL=
ENVIRONMENT=production
```

Optional backend variables:

```text
ADMIN_EMAILS=
LOG_LEVEL=INFO
SCORING_VERSION=mvp-2026-v1
```

### Health Checks

The backend `/health` endpoint should validate:

- The API process is running.
- Required settings loaded successfully.
- A lightweight database query succeeds.

Render should be configured with HTTP health checks against `/health`. The frontend can rely on Render's default web service check initially, but a lightweight Streamlit health route or separate readiness check can be added later if needed.

### Migrations

Use Alembic for PostgreSQL migrations.

Recommended production flow:

1. Build backend artifact.
2. Run `alembic upgrade head` against Neon as a controlled release step.
3. Deploy backend.
4. Deploy frontend if API contracts changed.

Avoid automatically running migrations inside every backend web process on startup. That can create race conditions when Render starts multiple instances.

### OAuth Configuration

Google Cloud OAuth client configuration should include:

- Authorized redirect URI for backend callback: `https://<api-domain>/api/v1/auth/google/callback`.
- Authorized JavaScript origins for the frontend and backend domains when required by Google configuration.
- Frontend callback URL allowlist enforced by backend settings.

The backend should reject OAuth redirect targets that are not in the configured allowlist.

### Operational Runbook

Initial release runbook:

1. Create Neon production database and copy the pooled or direct connection string.
2. Create backend Render service and configure backend environment variables.
3. Run migrations against Neon.
4. Confirm `/health` returns `200`.
5. Create frontend Render service and set `API_BASE_URL`.
6. Configure Google OAuth callback URLs using the deployed backend and frontend URLs.
7. Perform smoke test: login, create pool, join pool, submit prediction, enter result, verify ranking.

References consulted for deployment assumptions:

- Render FastAPI deployment: https://render.com/docs/deploy-fastapi
- Render health checks: https://render.com/docs/health-checks
- Render environment variables: https://render.com/docs/environment-variables
- Neon application connection strings: https://neon.com/docs/connect/connect-from-any-app
