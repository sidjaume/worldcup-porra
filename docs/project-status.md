# Project Status

Last updated: 2026-06-29

## Current Milestone

Milestone 4: Deployed MVP is in progress.

The repository now contains a working FastAPI backend, Next.js frontend, PostgreSQL schema/migration, Docker Compose local deployment, Render blueprint, and CI workflow. The canonical architecture/API/database/roadmap docs have been reconciled with that implementation state. REV-002 completed with changes requested, so the current state is not ready for merge.

## Completed

- Architecture/API/database/roadmap documentation reconciled with the current implementation state for ORCH-001; stale pre-implementation blocking language removed from core docs.
- Domain scoring, prediction lock, and bracket progression services with tests.
- Backend API surface for authentication, users, pools, tournaments, predictions, rankings, admin match operations, and `/health`.
- SQLAlchemy models, Alembic initial migration, repositories, and development seed script.
- Backend contract fixes completed for pool update response shape, standard request-validation error body, admin match completion/rescore documentation, and ranking tie-breaker alignment.
- DevOps/OAuth configuration audit completed: local defaults use Next.js/FastAPI ports, production settings require explicit URLs/secrets, and localhost production URLs are rejected.
- Next.js frontend with authenticated shell, pool workflows, prediction pages, rankings, profile, typed API client, and `/health`.
- Frontend server-side API URL precedence fixed so Docker server calls use `API_BASE_URL` while browser OAuth links use `NEXT_PUBLIC_API_BASE_URL`.
- Frontend UX/accessibility follow-up completed for mobile navigation, pool subnavigation, mobile rankings/participants, focus states, prediction status/labels, route loading/error states, form feedback, contrast, and invite-code rotation.
- Docker assets for backend and frontend, local `docker-compose.yml`, Render `render.yaml`, `.dockerignore`, `.env.example`, and deployment/environment/infrastructure docs.
- GitHub Actions workflow for backend checks, frontend checks, and Docker builds.
- Local Docker deployment verified with healthy PostgreSQL, backend, frontend, and migration service.
- BE-001 repository and migration integration coverage added with optional local/test PostgreSQL fixtures that create throwaway databases and skip safely when unavailable.
- DOCS-002 roadmap review-gate cleanup completed after REV-002.
- FE-007 pool creation invite-code and owner-control UX implementation completed.

## Verification Evidence

- REV-002 focused production-readiness re-review completed with `CHANGES_REQUESTED`.
- Backend lint: `.venv\Scripts\python.exe -m ruff check app tests` passed.
- Backend integration tests: `.venv\Scripts\python.exe -m pytest tests\db tests\repositories -q` passed, 4 tests.
- Backend tests: `.venv\Scripts\python.exe -m pytest tests -q` passed, 36 tests.
- Current session backend lint: `.\.venv\Scripts\python.exe -m ruff check app tests` passed.
- Current session backend tests: `.\.venv\Scripts\python.exe -m pytest tests -q` passed, 40 tests.
- BE-006 focused backend tests: worker ran `.venv\Scripts\python.exe -m pytest tests/services/test_pool_service.py tests/api/test_api_contract.py`, 13 tests passed.
- FE-007 source-level frontend tests were added for create action state, create form invite-code display, invite-code copy panel, and owner-only pool detail controls.
- Frontend lint: `npm run lint` passed.
- Frontend tests: `npm test` passed, 8 tests.
- Frontend typecheck: `npm run typecheck` passed.
- Frontend production build: previous `npm run build` passed; latest rerun after the most recent frontend/backend changes was not completed because the environment denied the required elevated filesystem access.
- Current session frontend checks were not run because this shell could not find `node` or `npm` on PATH.
- Local deployment: `docker compose ps` shows `db`, `backend`, and `frontend` running; backend `/health` returned `{"status":"ok","database":"ok"}`; frontend `/health` returned `{"status":"ok"}`.
- Frontend UX/accessibility follow-up: `npm test` passed, 12 tests; `npm run lint` passed; `npm run typecheck` passed.

## In Progress

- None.

## Changes Requested

- REV-002 completed with `CHANGES_REQUESTED`.
- DEVOPS-003: CI coverage for DB and repository integration tests.

## Planned

- DATA-EPIC-001 has been added for FIFA World Cup 2026 knockout data operations. The orchestrator should sequence this after REV-002 changes are resolved, starting with ARCH-003 to decide the data source/provider contract before backend, DevOps, admin UX, and frontend implementation begin.
- Planned task order: ARCH-003 data source and contract decision; BE-005 fixture import/provider sync backend; DEVOPS-002 sync operations; UX-002 admin correction flow; FE-006 admin match data UI; REV-003 full review.

## Blocked

- Production deployment is blocked until real Render, Neon, and Google OAuth secrets/configuration exist outside the repository.
- Merge readiness is blocked until REV-002 major findings are fixed and re-reviewed.
- Local Google OAuth testing is blocked unless Google OAuth credentials are configured. The local backend-owned callback is documented consistently as `http://localhost:8000/api/v1/auth/google/callback`.

## Pending Review

- BE-006 implementation is complete and backend-verified, but frontend validation is pending because this shell cannot run Node/NPM.
- FE-007 implementation is complete, but frontend validation is pending because this shell cannot run Node/NPM.
- Fixes for REV-002 findings after DEVOPS-003 is completed.
- ORCH-001 documentation reconciliation and the remaining documented database/service-enforced invariant gap remain pending final approval.

## Architect Findings

- BE-002 aligned the pool update response with the documented `PoolUpdated` shape.
- ARCH-002 resolved admin match operations as completion-only `PATCH` and `MatchRead` rescore response, and BE-003 aligned ranking final tie-breaker behavior and docs to earliest active participant join time.
- Database gap: several invariants are service-enforced rather than migration-enforced; Reviewer/Backend should decide whether that is acceptable for MVP.
- UX-001 requested frontend changes before production readiness.

## Ready For Merge

None. REV-002 requested changes.

## Production Status

Not deployed to production. Local Docker deployment is healthy.

## Next Recommended Task

Execute DEVOPS-003: CI coverage for DB and repository integration tests.

Rationale: BE-006 and FE-007 are implemented and awaiting frontend validation/review. DEVOPS-003 is the remaining unimplemented REV-002 major finding and is needed so CI covers the DB and repository integration tests before re-review.
