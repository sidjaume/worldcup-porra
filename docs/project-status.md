# Project Status

Last updated: 2026-06-29

## Current Milestone

Milestone 4: Deployed MVP is in progress.

The repository now contains a working FastAPI backend, Next.js frontend, PostgreSQL schema/migration, Docker Compose local deployment, Render blueprint, and CI workflow. The canonical architecture/API/database/roadmap docs have been reconciled with that implementation state, but the current state still needs independent Reviewer validation before it should be treated as ready for merge.

## Completed

- Architecture/API/database/roadmap documentation reconciled with the current implementation state for ORCH-001; stale pre-implementation blocking language removed from core docs.
- Domain scoring, prediction lock, and bracket progression services with tests.
- Backend API surface for authentication, users, pools, tournaments, predictions, rankings, admin match operations, and `/health`.
- SQLAlchemy models, Alembic initial migration, repositories, and development seed script.
- Backend contract fixes completed for pool update response shape, standard request-validation error body, admin match completion/rescore documentation, and ranking tie-breaker alignment.
- DevOps/OAuth configuration audit completed: local defaults use Next.js/FastAPI ports, production settings require explicit URLs/secrets, and localhost production URLs are rejected.
- Next.js frontend with authenticated shell, pool workflows, prediction pages, rankings, profile, typed API client, and `/health`.
- Frontend server-side API URL precedence fixed so Docker server calls use `API_BASE_URL` while browser OAuth links use `NEXT_PUBLIC_API_BASE_URL`.
- Docker assets for backend and frontend, local `docker-compose.yml`, Render `render.yaml`, `.dockerignore`, `.env.example`, and deployment/environment/infrastructure docs.
- GitHub Actions workflow for backend checks, frontend checks, and Docker builds.
- Local Docker deployment verified with healthy PostgreSQL, backend, frontend, and migration service.
- BE-001 repository and migration integration coverage added with optional local/test PostgreSQL fixtures that create throwaway databases and skip safely when unavailable.

## Verification Evidence

- Backend lint: `.venv\Scripts\python.exe -m ruff check app tests` passed.
- Backend integration tests: `.venv\Scripts\python.exe -m pytest tests\db tests\repositories -q` passed, 4 tests.
- Backend tests: `.venv\Scripts\python.exe -m pytest tests -q` passed, 36 tests.
- Frontend lint: `npm run lint` passed.
- Frontend tests: `npm test` passed, 8 tests.
- Frontend typecheck: `npm run typecheck` passed.
- Frontend production build: previous `npm run build` passed; latest rerun after the most recent frontend/backend changes was not completed because the environment denied the required elevated filesystem access.
- Local deployment: `docker compose ps` shows `db`, `backend`, and `frontend` running; backend `/health` returned `{"status":"ok","database":"ok"}`; frontend `/health` returned `{"status":"ok"}`.

## In Progress

- Focused production-readiness re-review after technical fixes.
- Frontend UX/accessibility follow-up tasks from Product Designer review.

## Blocked

- Production deployment is blocked until real Render, Neon, and Google OAuth secrets/configuration exist outside the repository.
- Merge readiness is blocked until the Reviewer completes a focused re-review and frontend UX/accessibility changes requested by Product Designer are resolved or explicitly deferred.
- Local Google OAuth testing is blocked unless Google OAuth credentials are configured. The local backend-owned callback is documented consistently as `http://localhost:8000/api/v1/auth/google/callback`.

## Pending Review

- Backend implementation and tests.
- Frontend UX/accessibility follow-up tasks: mobile navigation, mobile rankings/participants, focus-visible states, prediction labeling/status handling, route-level loading/error states, announced feedback, contrast, invite-code rotation safety, and ranking label clarity.
- DevOps deployment assets, CI, and environment documentation.
- ORCH-001 documentation reconciliation and the remaining documented database/service-enforced invariant gap.

## Architect Findings

- BE-002 aligned the pool update response with the documented `PoolUpdated` shape.
- ARCH-002 resolved admin match operations as completion-only `PATCH` and `MatchRead` rescore response, and BE-003 aligned ranking final tie-breaker behavior and docs to earliest active participant join time.
- Database gap: several invariants are service-enforced rather than migration-enforced; Reviewer/Backend should decide whether that is acceptable for MVP.
- UX-001 requested frontend changes before production readiness.

## Ready For Merge

None. The working tree contains broad uncommitted changes and requires specialist review.

## Production Status

Not deployed to production. Local Docker deployment is healthy.

## Next Recommended Task

Execute the READY frontend UX/accessibility backlog tasks, then run focused Reviewer re-review.

Rationale: Technical contract/config/test gaps from REV-001 have been addressed. The remaining unblocked work is frontend UX/accessibility polish required by Product Designer before production readiness.
