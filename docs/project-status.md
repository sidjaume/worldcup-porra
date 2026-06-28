# Project Status

Last updated: 2026-06-29

## Current Milestone

Milestone 4: Deployed MVP is in progress.

The repository now contains a working FastAPI backend, Next.js frontend, PostgreSQL schema/migration, Docker Compose local deployment, Render blueprint, and CI workflow. The canonical architecture/API/database/roadmap docs still carry draft review warnings, so the current state needs architecture/reviewer reconciliation before it should be treated as ready for merge.

## Completed

- Architecture/API/database/roadmap documentation reconciled with the current implementation state for ORCH-001; stale "implementation must not begin" language removed from core docs.
- Domain scoring, prediction lock, and bracket progression services with tests.
- Backend API surface for authentication, users, pools, tournaments, predictions, rankings, admin match operations, and `/health`.
- SQLAlchemy models, Alembic initial migration, repositories, and development seed script.
- Next.js frontend with authenticated shell, pool workflows, prediction pages, rankings, profile, typed API client, and `/health`.
- Docker assets for backend and frontend, local `docker-compose.yml`, Render `render.yaml`, `.dockerignore`, `.env.example`, and deployment/environment/infrastructure docs.
- GitHub Actions workflow for backend checks, frontend checks, and Docker builds.
- Local Docker deployment verified with healthy PostgreSQL, backend, frontend, and migration service.

## Verification Evidence

- Backend lint: `python -m ruff check app tests` passed.
- Backend tests: `python -m pytest tests` passed, 21 tests.
- Frontend lint: `npm run lint` passed.
- Frontend tests: `npm test` passed, 5 tests.
- Frontend typecheck: `npm run typecheck` passed.
- Frontend production build: `npm run build` passed.
- Local deployment: `docker compose ps` shows `db`, `backend`, and `frontend` running; backend `/health` returned `{"status":"ok","database":"ok"}`; frontend `/health` returned `{"status":"ok"}`.

## In Progress

- Independent review of the accumulated backend, frontend, DevOps, and docs changes.
- Production configuration readiness for Render, Neon, and Google OAuth.

## Blocked

- Production deployment is blocked until real Render, Neon, and Google OAuth secrets/configuration exist outside the repository.
- Merge readiness is blocked until the Reviewer completes an independent review and contract gaps from ORCH-001 are accepted or converted into specialist fixes.
- Local Google OAuth testing is blocked unless Google OAuth credentials are configured. `.env.example` also needs review because its `GOOGLE_REDIRECT_URI` uses the frontend host (`localhost:3000`) with the backend OAuth callback path, while the backend-owned OAuth contract and Docker Compose use the backend host (`localhost:8000`).

## Pending Review

- Backend implementation and tests.
- Frontend implementation and accessibility/usability.
- DevOps deployment assets, CI, and environment documentation.
- ORCH-001 documentation reconciliation and the documented API/database contract gaps.

## Architect Findings

- API contract gap: pool update response currently omits `is_active` despite the documented example.
- API contract gap: admin match patch endpoint is implemented as completion-only, while the contract describes broader match update capability.
- API contract gap: rescore endpoint returns `MatchRead`; the contract now notes this implemented behavior but needs explicit approval.
- Database/API gap: ranking final tie-breaker is implemented as display name, while database docs recommend earliest joined participant.
- Database gap: several invariants are service-enforced rather than migration-enforced; Reviewer/Backend should decide whether that is acceptable for MVP.
- DevOps/Backend gap: OAuth callback environment examples and settings defaults need cleanup.

## Ready For Merge

None. The working tree contains broad uncommitted changes and requires specialist review.

## Production Status

Not deployed to production. Local Docker deployment is healthy.

## Next Recommended Task

Run the independent Reviewer quality gate, then route findings to Backend, Frontend, or DevOps.

Rationale: ORCH-001 removed the stale pre-implementation contradiction and made contract gaps explicit. The next decision should come from an independent production-readiness review before new feature work begins.
