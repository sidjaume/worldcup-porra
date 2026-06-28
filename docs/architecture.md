# Architecture

Status: Implementation exists and is pending architecture/reviewer reconciliation.
Last reconciled: 2026-06-29.

This document remains the target architecture and contract governance source. It
no longer blocks implementation from beginning; instead, it records the intended
architecture, the implemented MVP slices currently present in the repository,
and the gaps that need specialist follow-up before merge or production release.

## Purpose

This application is a private FIFA World Cup 2026 knockout prediction pool. It manages only the completed-tournament knockout bracket:

- Round of 32
- Round of 16
- Quarter-finals
- Semi-finals
- Final

The application does not model group stage standings, group predictions, qualification rules, or team qualification calculations.

## System Architecture

The MVP uses a modular monolith split into two deployable processes. The current
repository already contains this shape:

- Backend: FastAPI REST API, domain services, repositories, migrations, and authentication.
- Frontend: Next.js application that renders the user experience and talks to the backend through HTTP APIs.
- Database: Neon PostgreSQL, accessed only by backend repositories.

```text
Browser
  |
  v
Render Web Service: Next.js frontend
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

## Current Implementation Snapshot

As of this reconciliation pass, the repository includes:

- FastAPI backend under `app/` with routers for auth, users, pools, tournaments, predictions, rankings, admin match operations, and `/health`.
- Domain services for scoring, prediction locking, and bracket progression.
- Application services and SQLAlchemy repositories for auth, pools, tournaments, predictions, rankings, and admin result workflows.
- SQLAlchemy models and an Alembic initial migration for users, OAuth accounts, tournaments, teams, matches, pools, participants, predictions, prediction scores, auth sessions, and auth exchange codes.
- Next.js frontend under `frontend/` with authenticated pool, prediction, ranking, profile, callback, refresh, logout, and health routes.
- Dockerfiles, Docker Compose local stack, Render blueprint, CI workflow, and environment documentation.

Implementation status is not equivalent to production approval. The current
state still requires independent Reviewer assessment, Backend/Frontend/DevOps
follow-ups listed in `docs/backlog.md`, and production secret/configuration
work before deployment.

## Architectural Principles

- Keep business rules independent from FastAPI, frontend framework code, PostgreSQL, and Google OAuth.
- Treat the domain layer as the source of truth for scoring, prediction locks, and knockout progression rules.
- Use repositories for all database access.
- Keep frontend components thin: UI state, forms, rendering, and API client calls only.
- Use migrations for every database schema change.
- Prefer explicit, simple service classes over broad abstractions.
- Design for 10-100 users per pool first, while avoiding choices that block later growth.

## Architecture Decisions

### ADR-001: Modular Monolith

Decision: Use a modular monolith with clear internal boundaries.

Rationale:

- The MVP is small enough that microservices would add operational cost without product value.
- Domain rules remain testable when kept separate from API, persistence, and UI code.
- A single backend deployment is simpler for Render and Neon.

Rejected alternatives:

- Microservices: premature for 10-100 users per private pool.
- Direct frontend-to-database access: violates security and business-rule boundaries.

### ADR-002: Backend-Owned Business Rules

Decision: Backend owns authentication, authorization, prediction locking, scoring, bracket progression, rankings, and persistence.

Rationale:

- Prevents frontend/backend divergence.
- Makes scoring and locking independently testable.
- Keeps private pool membership authorization enforceable.

Frontend responsibility is presentation, navigation, local UI state, and backend API calls.

### ADR-003: Backend-Owned Google OAuth

Decision: Google OAuth redirects and Google token exchange are handled by FastAPI.

Rationale:

- Google client secret must never be exposed to the frontend.
- User provisioning and application token issuance are backend concerns.
- The same contract works for both local prototype and production frontend.

### ADR-004: PostgreSQL With Alembic

Decision: Use PostgreSQL through repositories and manage schema changes with Alembic migrations.

Rationale:

- Neon is the target managed database.
- Constraints, indexes, UUIDs, and transactional migrations are required for reproducibility.
- PostgreSQL keeps the MVP cloud-ready.

### ADR-005: Next.js Production Frontend

Decision: The production frontend target is Next.js, React, TypeScript, and Tailwind CSS.

Rationale:

- Matches the current project constitution and architect deployment target.
- Supports responsive web UX and maintainable component structure.
- Keeps the frontend deployable as an independent Render service.

The earlier Streamlit prototype has been removed. Product-facing frontend work
targets the Next.js structure below.

## Backend Module Structure

Current implemented structure:

```text
app/
  api/
    main.py
    dependencies.py
    errors.py
    routers/
      auth.py
      users.py
      pools.py
      tournaments.py
      predictions.py
      rankings.py
      admin.py
    schemas/
      auth.py
      admin.py
      users.py
      pools.py
      tournaments.py
      predictions.py
  config/
    settings.py
  domain/
    entities/
      scoring.py
    enums.py
    errors.py
    services/
      scoring_engine.py
      prediction_policy.py
      bracket_progression.py
  services/
    auth_service.py
    pool_service.py
    tournament_service.py
    prediction_service.py
    admin_service.py
    security.py
  repositories/
    users.py
    oauth_accounts.py
    pools.py
    tournaments.py
    predictions.py
    auth.py
  models/
    base.py
    user.py
    pool.py
    participant.py
    tournament.py
    team.py
    match.py
    prediction.py
    auth.py
  db/
    session.py
    migrations/
tests/
  domain/
  services/
  api/
```

Architectural note: participants, matches, rankings, and scores are currently
handled inside the pool, tournament, prediction, and admin modules rather than
as separate router/repository files. That is acceptable for the MVP modular
monolith as long as responsibilities stay cohesive and do not push business
rules into routers or frontend code.

### Backend Responsibilities

`api`
: FastAPI application setup, request/response schemas, routers, dependencies, middleware, and exception mapping.

`domain`
: Pure Python rules for scoring, prediction lock checks, match outcome interpretation, and bracket advancement. This layer must not import FastAPI, SQLAlchemy, Next.js/React code, Streamlit, Google clients, or settings.

`services`
: Application use cases. Services coordinate repositories, domain rules, authorization checks, and transaction boundaries.

`repositories`
: SQL persistence. Repositories should expose intent-focused methods rather than leaking query details into services.

`models`
: SQLAlchemy ORM models that map to PostgreSQL tables.

`config`
: Environment-based settings, logging, CORS, token configuration, and external provider configuration.

## Domain Boundaries

The implemented boundary is broadly aligned with the target model: scoring,
lock checks, and bracket progression live under `app/domain`, while FastAPI
routers coordinate request handling through application services. Continued
Reviewer scrutiny is still needed for transaction boundaries, authorization
coverage, and error consistency.

## Domain Model

Core domain concepts:

- User: authenticated person with a Google-linked account.
- Tournament: FIFA World Cup 2026 knockout tournament container.
- Team: national team in the knockout bracket.
- Match: knockout fixture with scheduled time, status, teams, score, winner, and optional next-match progression link.
- Pool: private prediction group owned by one user.
- Participant: user's membership in a pool, including role and active/removed status.
- Prediction: participant's predicted score for one pool-specific match.
- PredictionScore: persisted result of applying the scoring engine to a prediction.
- Ranking: derived aggregate view of prediction scores per pool.

Domain invariants:

- Predictions are scoped to `(pool, user, match)`.
- A user must be an active pool participant to submit or view pool-specific data.
- Predictions cannot be created or edited after backend lock time.
- Scoring is calculated by the domain scoring engine, not by UI code.
- A completed knockout match must have a winner.
- Winner progression uses explicit `next_match_id` and `next_match_slot` links.
- Rankings are derived from scores and must not be manually edited.

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

Target frontend stack:

- Next.js
- React
- TypeScript
- Tailwind CSS

Frontend work targets the implemented Next.js structure below. Some component
names differ from the earlier target sketch, but the ownership boundary remains:
the frontend renders UI and calls documented APIs; backend remains the source
of truth for business rules.

```text
frontend/
  app/
    layout.tsx
    page.tsx
    auth/
      callback/
        route.ts
      refresh/
        route.ts
    logout/
      route.ts
    pools/
      page.tsx
      [poolId]/
        page.tsx
        predictions/
          page.tsx
        rankings/
          page.tsx
    profile/
      page.tsx
  components/
    auth/
      LoginButton.tsx
      UserMenu.tsx
    pools/
      PoolDashboard.tsx
      PoolSelector.tsx
      CreatePoolForm.tsx
      JoinPoolForm.tsx
    predictions/
      MatchPredictionCard.tsx
      PredictionForm.tsx
      StageTabs.tsx
    rankings/
      RankingTable.tsx
    layout/
      AppShell.tsx
    profile/
      ProfileForm.tsx
  lib/
    api/
      client.ts
      auth.ts
      pools.ts
      tournaments.ts
      predictions.ts
      rankings.ts
    auth/
      session.ts
      tokens.ts
    config.ts
  types/
    api.ts
  styles/
    globals.css
```

### Frontend Responsibilities

- Render dashboard, pools, predictions, rankings, and profile screens.
- Store application auth state securely for the web client. Prefer server-side/session-cookie storage for refresh tokens; avoid localStorage for refresh tokens.
- Call backend APIs through a small typed API client under `frontend/lib/api`.
- Show backend validation errors clearly.
- Avoid direct database access.
- Avoid scoring, locking, and bracket progression logic.
- Use responsive, mobile-first layouts.
- Keep Tailwind usage component-scoped and avoid one-off visual drift.

## Frontend/Backend Contract

The API contract is owned by the architect and defined in `docs/api.md`.

Frontend promises:

- Call only documented `/api/v1` endpoints.
- Send access tokens using `Authorization: Bearer <token>`.
- Treat backend error responses as the source of truth for validation and authorization messages.
- Never calculate scoring, prediction locks, rankings, or bracket progression.
- Never connect directly to PostgreSQL.

Backend promises:

- Preserve documented endpoint names, request bodies, response bodies, and error format unless the API contract is reviewed.
- Enforce authorization and business rules independently of frontend behavior.
- Return predictable status codes and machine-readable error codes.
- Keep OAuth client secrets server-side only.

Contract changes require:

1. Update `docs/api.md`.
2. Review by architect.
3. Backend implementation.
4. Frontend adaptation.
5. Smoke test of affected flow.

### Initial Screens

- Dashboard: active pools, selected pool summary, participant count, and next matches.
- Pools: create pool, join pool by invite code, participant list, invite-code actions for owners.
- Predictions: match list by round, prediction forms for unlocked matches, read-only state for locked/completed matches.
- Rankings: pool ranking table with points and prediction counts.
- Profile: user display name and account details.

### Frontend Implementation Notes

- Do not move scoring, lock, ranking, bracket, or membership rules into the frontend.
- Reuse the existing REST API contract.
- Keep route-level data loading close to pages and shared request logic in `frontend/lib/api`.
- Keep auth callback behavior compatible with `/api/v1/auth/google/start`, `/api/v1/auth/google/callback`, and `/api/v1/auth/exchange`.

## Reconciliation Findings

Open architecture/API/database questions are tracked as follow-up work rather
than being silently changed in code:

- Backend: ranking tie-breakers in implementation currently sort by total points, exact scores, correct winners, then display name; `docs/database.md` originally recommended earliest joined participant as the final tie-breaker.
- Backend/API: pool update currently returns the pool detail shape without `is_active`, while the API contract example includes `is_active`.
- Backend/API: admin `PATCH /api/v1/admin/matches/{match_id}` is currently a match-completion endpoint accepting scores and winner only; the API text describes broader schedule/team/status updates.
- Backend/API: `POST /api/v1/admin/matches/{match_id}/rescore` currently returns `MatchRead`; the contract should explicitly approve that response or define a scoring-specific response.
- Database: several invariants are enforced in services rather than database constraints, including completed-match winner/scores, final `next_match_id` rules, and pool/match tournament consistency for predictions.
- DevOps/Backend: `.env.example` sets `GOOGLE_REDIRECT_URI` to the frontend host with the backend callback path, while Docker Compose uses the backend host callback. The backend-owned OAuth callback contract should be confirmed and the environment examples aligned.
- DevOps/Backend: `app/config/settings.py` default frontend origin still references the older `localhost:8501`; runtime examples override this to `localhost:3000`, but defaults should be cleaned up by the owning specialist.

These gaps do not require an architecture redesign. They require contract
decisions and focused Backend, Frontend, or DevOps follow-up tasks before the
Reviewer can recommend merge or production readiness.

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
- Render service 2: Next.js frontend web service.
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
  process: Next.js app
  build command example: npm ci && npm run build
  start command example: npm run start -- --hostname 0.0.0.0 --port $PORT
```

Use Docker for reproducible production builds once the project has dependencies and entrypoints. Native Render services are acceptable during early MVP development, but Docker should be the production target because it keeps local and cloud runtime behavior closer.

### Neon Database

Create one Neon project for production and use a PostgreSQL connection string exposed as `DATABASE_URL` to the backend. Neon connection strings should require SSL. Use separate Neon branches or separate projects for development/staging if collaborative testing needs isolated data.

The frontend service must not receive `DATABASE_URL`.

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
NEXT_PUBLIC_API_BASE_URL=
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

Render should be configured with HTTP health checks against `/health` for both
the backend and the Next.js frontend.

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
5. Create frontend Render service and set `NEXT_PUBLIC_API_BASE_URL`.
6. Configure Google OAuth callback URLs using the deployed backend and frontend URLs.
7. Perform smoke test: login, create pool, join pool, submit prediction, enter result, verify ranking.

References consulted for deployment assumptions:

- Render FastAPI deployment: https://render.com/docs/deploy-fastapi
- Render health checks: https://render.com/docs/health-checks
- Render environment variables: https://render.com/docs/environment-variables
- Neon application connection strings: https://neon.com/docs/connect/connect-from-any-app
