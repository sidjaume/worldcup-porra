# Project Status

Last updated: 2026-06-29

## Current Milestone

Milestone 4: Deployed MVP is in progress.

The repository now contains a working FastAPI backend, Next.js frontend, PostgreSQL schema/migration, Docker Compose local deployment, Render blueprint, and CI workflow. The canonical architecture/API/database/roadmap docs have been reconciled with that implementation state. REV-002's split follow-up tasks were implemented, reviewed, and recorded in the backlog as historical follow-up work.

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
- Windows Node/NPM invocation documented in `AGENTS.md` and `docs/environment.md`.
- ORCH-001 `POST /api/v1/pools` contract correction approved by Reviewer with comments.
- BE-006 inactive-pool reactivation UX fix approved by Reviewer.
- DEVOPS-003 CI coverage for DB and repository integration tests approved by Reviewer.
- ARCH-003 accepted for knockout data source and result semantics.
- ARCH-003 selects `rezarahiminia/worldcup2026` as the preferred initial free data-source candidate for DATA-EPIC-001, with import/self-hosting preferred over blind public-host dependency.

## Verification Evidence

- REV-002 focused production-readiness re-review completed with `CHANGES_REQUESTED`, then its follow-up tasks were approved and the closure review was rerun.
- Backend lint: `.venv\Scripts\python.exe -m ruff check app tests` passed.
- Backend integration tests: `.venv\Scripts\python.exe -m pytest tests\db tests\repositories -q` passed, 4 tests.
- Backend tests: `.venv\Scripts\python.exe -m pytest tests -q` passed, 36 tests.
- Current session backend lint: `.\.venv\Scripts\python.exe -m ruff check app tests` passed.
- Current session backend tests: `.\.venv\Scripts\python.exe -m pytest tests -q` passed, 40 tests.
- BE-006 focused backend tests: worker ran `.venv\Scripts\python.exe -m pytest tests/services/test_pool_service.py tests/api/test_api_contract.py`, 13 tests passed.
- FE-007 source-level frontend tests were added for create action state, create form invite-code display, invite-code copy panel, and owner-only pool detail controls.
- Current session frontend lint: `npm.cmd run lint` passed with documented Windows PATH prefix.
- Current session frontend tests: `npm.cmd test` passed, 13 files and 17 tests.
- Current session frontend typecheck: `npm.cmd run typecheck` passed after elevated rerun for `.next/types` writes.
- Current session frontend build: `npm.cmd run build` passed after elevated rerun for `.next` writes.
- ORCH-001 contract check: `.venv\Scripts\python.exe -m pytest tests\api\test_api_contract.py -q` passed, 6 tests.
- ORCH-001 full backend tests: `.venv\Scripts\python.exe -m pytest tests -q` passed, 41 tests.
- ORCH-001 focused frontend tests passed with `npm.cmd test -- app/actions.test.ts components/pools/CreatePoolForm.test.ts components/pools/InviteCodeForm.test.ts app/pools/[poolId]/page.test.ts components/pools/PoolSettingsForm.test.ts`.
- BE-006 UX fix frontend lint: `npm.cmd run lint` passed.
- BE-006 UX fix focused frontend tests: `npm.cmd test -- app/actions.test.ts components/pools/PoolSettingsForm.test.ts` passed, 2 files and 3 tests.
- BE-006 UX fix frontend typecheck: `npm.cmd run typecheck` passed after elevated rerun for `.next/types` writes.
- BE-006 UX fix backend checks: Ruff passed and `.venv\Scripts\python.exe -m pytest tests -q` passed, 41 tests.
- DEVOPS-003 backend lint: `.\.venv\Scripts\python.exe -m ruff check app tests` passed.
- DEVOPS-003 backend compile check: `.\.venv\Scripts\python.exe -m compileall app tests` passed.
- DEVOPS-003 updated backend test matrix: `.\.venv\Scripts\python.exe -m pytest tests/api tests/config tests/domain tests/services tests/db tests/repositories -q` passed, 41 tests.
- DEVOPS-003 workflow YAML parse check passed with `yaml.safe_load`.
- DEVOPS-003 focused Reviewer decision: `APPROVED`.
- Pending-review backend lint: `.\.venv\Scripts\python.exe -m ruff check app tests` passed.
- Pending-review backend tests: `.\.venv\Scripts\python.exe -m pytest tests -q` passed, 41 tests.
- Pending-review focused frontend tests: `npm.cmd test -- app/actions.test.ts components/pools/PoolSettingsForm.test.ts components/pools/CreatePoolForm.test.ts components/pools/InviteCodeForm.test.ts app/pools/[poolId]/page.test.ts` passed, 5 files and 6 tests.
- Pending-review frontend lint: `npm.cmd run lint` passed.
- Pending-review frontend typecheck: `npm.cmd run typecheck` passed after elevated rerun for `.next/types` writes.
- ORCH-001 focused Reviewer decision: `APPROVED WITH COMMENTS`; comment addressed by removing stale verification notes from this status file.
- BE-006 focused Reviewer decision: `APPROVED`.
- Local deployment: `docker compose ps` shows `db`, `backend`, and `frontend` running; backend `/health` returned `{"status":"ok","database":"ok"}`; frontend `/health` returned `{"status":"ok"}`.
- Frontend UX/accessibility follow-up: `npm test` passed, 12 tests; `npm run lint` passed; `npm run typecheck` passed.

## In Progress

- None.

## Changes Requested

None.

## Planned

- Planned execution order for DATA-EPIC-001: BE-005 fixture import/provider sync backend; DEVOPS-002 sync operations; UX-002 admin correction flow; FE-006 admin match data UI; REV-003 full review.

## Blocked

- Production deployment is blocked until real Render, Neon, and Google OAuth secrets/configuration exist outside the repository.
- Local Google OAuth testing is blocked unless Google OAuth credentials are configured. The local backend-owned callback is documented consistently as `http://localhost:8000/api/v1/auth/google/callback`.
- Provider-backed sync execution for DATA-EPIC-001 still depends on the project owner deciding provider budget/licensing constraints and supplying account credentials.

## Pending Review

None.

## Architect Findings

- BE-002 aligned the pool update response with the documented `PoolUpdated` shape.
- ARCH-002 resolved admin match operations as completion-only `PATCH` and `MatchRead` rescore response, and BE-003 aligned ranking final tie-breaker behavior and docs to earliest active participant join time.
- Database gap: several invariants are service-enforced rather than migration-enforced; Reviewer/Backend should decide whether that is acceptable for MVP.
- UX-001 requested frontend changes before production readiness.

## Ready For Merge

None. REV-002 follow-up work is approved and archived in the backlog.

## Production Status

Not deployed to production. Local Docker deployment is healthy.

## Next Recommended Task

Start BE-005 against the `worldcup2026` import/adapter path.

Rationale: ARCH-003 is accepted and gives DATA-EPIC-001 a stable architecture, execution order, and realistic free candidate source. BE-005 can now align backend result semantics and build the import/sync adapter.
