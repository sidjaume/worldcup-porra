# Project Status

Last updated: 2026-06-30

## Current Milestone

Milestone 4: Deployed MVP is in progress.

The repository now contains a working FastAPI backend, Next.js frontend, PostgreSQL schema/migration, Docker Compose local deployment, Render blueprint, and CI workflow. The canonical architecture/API/database/roadmap docs have been reconciled with that implementation state. REV-002's split follow-up tasks were implemented, reviewed, and recorded in the backlog as historical follow-up work. DATA-EPIC-001 has backend and sync-operations slices implemented and approved by the independent Reviewer gate.

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
- BE-005 fixture import/provider sync backend implemented and approved by independent Reviewer gate.
- DEVOPS-002 tournament data sync operations implemented and approved by independent Reviewer gate.
- UX-002 admin correction and sync visibility flow specified for FE-006.
- FE-006 admin match data management UI approved with comments by independent Reviewer gate.
- ARCH-004 knockout operations remediation contract accepted and synchronized across API, database, frontend, deployment, infrastructure, environment, backlog, and status docs.
- BE-008 tied prediction advancing-winner backend semantics implemented and approved with comments by independent Reviewer gate.
- BE-009 admin team/status correction fallback implemented and approved by independent Reviewer gate.
- BE-007 provider sync manual override protection implemented and approved by independent Reviewer gate.
- BE-010 provider normalization fail-closed hardening implemented and approved by independent Reviewer gate.
- DEVOPS-004 free-plan sync operations runbook approved by independent Reviewer gate.
- FE-008 match status contract alignment approved with comments by independent Reviewer gate.
- FE-009 tied prediction and admin correction UI alignment approved with comments by independent Reviewer gate.
- REV-003 knockout data operations re-review approved with comments by independent Reviewer gate.
- DEVOPS-005 free-plan Render blueprint cron cleanup approved by independent Reviewer gate.

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
- BE-005 backend lint: `.\.venv\Scripts\python.exe -m ruff check app tests scripts` passed.
- BE-005 focused regression matrix: `.\.venv\Scripts\python.exe -m pytest tests/providers/test_worldcup2026_adapter.py tests/services/test_fixture_sync_service.py tests/services/test_admin_service.py tests/scripts/test_sync_knockout_fixtures.py` passed, 12 tests.
- BE-005 backend/script matrix: `.\.venv\Scripts\python.exe -m pytest tests/api tests/config tests/domain tests/services tests/providers tests/db tests/repositories tests/scripts` passed, 53 tests.
- BE-005/DEVOPS-002 independent Reviewer gate: no blocking issues found; residual runtime validation gaps are the first live provider response shape and actual scheduled-sync execution.
- DEVOPS-002 YAML parse: `render.yaml` and `docker-compose.yml` parsed successfully with `yaml.safe_load`.
- DEVOPS-002 Compose validation: `docker compose --env-file .env.example --profile tools config` rendered successfully.
- DEVOPS-002 config tests: `.\.venv\Scripts\python.exe -m pytest tests\config` passed, 4 tests.
- DEVOPS-002 whitespace check: `git diff --check` passed with only Windows LF/CRLF warnings.
- UX-002 documentation-only verification: `docs/frontend.md` now defines the admin operator flow, sync visibility, correction forms, confirmation/error states, accessibility requirements, responsive behavior, and FE-006 API data needs. No automated tests were required for this design-only task; FE-006 is expected to add component, route, and API-client tests.
- FE-006 frontend lint: `npm.cmd run lint` passed.
- FE-006 frontend tests: `npm.cmd test` passed, 17 files and 34 tests.
- FE-006 frontend typecheck: `npm.cmd run typecheck` passed after elevated rerun for `.next/types` writes.
- FE-006 frontend build: `npm.cmd run build` passed after elevated rerun for `.next` writes.
- FE-006 Reviewer gate: initial decision `CHANGES_REQUESTED`; follow-up fixed admin mutation `403` no-controls state and missing route tournament empty state; re-review decision `APPROVED WITH COMMENTS`.
- REV-003 full knockout data operations review decision: `CHANGES_REQUESTED`.
- ARCH-004 documentation-only verification: [ARCH-004 ADR](./decisions/arch-004-knockout-operations-remediation-contract.md) accepted the minimal remediation contract for tied prediction advancing winners, admin team/status correction endpoints, manual override protection, provider fail-closed normalization, and free-plan sync operations. No automated tests were required.
- BE-008 backend checks: `.\.venv\Scripts\python.exe -m pytest` passed, 63 tests; `.\.venv\Scripts\python.exe -m ruff check .` passed. Independent Reviewer reproduced focused checks with 27 tests plus Ruff on app/tests and returned `APPROVED WITH COMMENTS`.
- BE-009 focused backend checks: `.\.venv\Scripts\python.exe -m pytest tests/services/test_admin_service.py tests/api/test_api_contract.py` passed, 27 tests; `.\.venv\Scripts\python.exe -m ruff check app/api/routers/admin.py app/api/schemas/admin.py app/services/admin_service.py tests/services/test_admin_service.py tests/api/test_api_contract.py` passed.
- BE-009 full backend checks: `.\.venv\Scripts\python.exe -m pytest` passed, 79 tests; `.\.venv\Scripts\python.exe -m ruff check .` passed.
- BE-009 independent Reviewer gate: `APPROVED`.
- BE-007 focused backend checks: `.\.venv\Scripts\python.exe -m pytest tests/services/test_admin_service.py tests/services/test_fixture_sync_service.py -q` passed, 27 tests; `.\.venv\Scripts\python.exe -m ruff check app/services/admin_service.py app/services/fixture_sync_service.py tests/services/test_admin_service.py tests/services/test_fixture_sync_service.py` passed.
- BE-007 full backend checks: `.\.venv\Scripts\python.exe -m pytest -q` passed, 84 tests; `.\.venv\Scripts\python.exe -m ruff check .` passed.
- BE-007 independent Reviewer gate: `APPROVED`.
- BE-010 focused backend checks: `.\.venv\Scripts\python.exe -m pytest tests\providers\test_worldcup2026_adapter.py tests\services\test_fixture_sync_service.py -q` passed, 18 tests; `.\.venv\Scripts\python.exe -m ruff check app\providers\worldcup2026.py tests\providers\test_worldcup2026_adapter.py tests\services\test_fixture_sync_service.py` passed.
- BE-010 full backend checks: `.\.venv\Scripts\python.exe -m pytest -q` passed, 91 tests; `.\.venv\Scripts\python.exe -m ruff check .` passed.
- BE-010 independent Reviewer gate: `APPROVED`.
- DEVOPS-004 docs/config sanity: `render.yaml` and `docker-compose.yml` parsed
  successfully with `yaml.safe_load`.
- DEVOPS-004 CLI syntax sanity: `.\.venv\Scripts\python.exe -m scripts.sync_knockout_fixtures --help` returned usage successfully without requiring production secrets.
- DEVOPS-004 docs consistency grep: Render cron references in deployment,
  infrastructure, environment, backlog, and status docs now describe it as
  optional/plan-dependent, with local/operator scheduled sync against Neon as
  the free-plan path.
- DEVOPS-004 independent Reviewer gate: `APPROVED`.
- FE-008 focused frontend tests: `npm.cmd test -- components/admin/AdminOperations.test.ts components/predictions/MatchPredictionCard.test.ts` passed, 2 files and 11 tests.
- FE-008 frontend lint: `npm.cmd run lint` passed.
- FE-008 frontend tests: `npm.cmd test` passed, 18 files and 37 tests.
- FE-008 frontend typecheck: `npm.cmd run typecheck` passed after elevated rerun for `.next/types` writes.
- FE-008 independent Reviewer gate: `APPROVED WITH COMMENTS`.
- FE-009 focused frontend tests: `npm.cmd test -- app/actions.test.ts app/admin/actions.test.ts lib/api/admin.test.ts lib/api/predictions.test.ts components/admin/AdminOperations.test.ts components/predictions/MatchPredictionCard.test.ts` passed, 6 files and 26 tests.
- FE-009 frontend tests: `npm.cmd test` passed, 19 files and 44 tests.
- FE-009 frontend lint: `npm.cmd run lint` passed.
- FE-009 frontend typecheck: `npm.cmd run typecheck` passed after elevated rerun for `.next/types` writes.
- FE-009 independent Reviewer gate: `APPROVED WITH COMMENTS`.
- REV-003 re-review readiness backend checks: `.\.venv\Scripts\python.exe -m pytest` passed, 91 tests; `.\.venv\Scripts\python.exe -m ruff check .` passed.
- REV-003 Reviewer re-review focused backend checks: 61 tests passed; focused Ruff passed.
- REV-003 re-review decision: `APPROVED WITH COMMENTS`. Non-blocking follow-up: `DEVOPS-005` should ensure the default free-plan Render blueprint does not accidentally provision the optional cron service.
- DEVOPS-005 YAML parse: `.\.venv\Scripts\python.exe -c "import yaml, pathlib; data=yaml.safe_load(pathlib.Path('render.yaml').read_text()); services=data.get('services', []); print('render.yaml parsed'); print('service_count=', len(services)); print('service_types=', ','.join(s.get('type','') for s in services)); print('service_names=', ','.join(s.get('name','') for s in services))"` passed with `service_count= 2`, `service_types= web,web`, and `service_names= worldcup-pool-api,worldcup-pool-frontend`.
- DEVOPS-005 blueprint cron grep: `rg -n 'type:\s*cron' render.yaml` returned no matches.
- DEVOPS-005 stale docs grep returned no matches for prior statements that the
  default Render blueprint defines a cron service.
- DEVOPS-005 free-plan docs grep found the updated default-blueprint/free-plan guidance in deployment and infrastructure docs.
- DEVOPS-005 scoped whitespace check: `git diff --check -- render.yaml docs/deployment.md docs/infrastructure.md docs/environment.md docs/project-status.md docs/backlog.md` passed with LF/CRLF warnings only.
- DEVOPS-005 independent Reviewer gate: `APPROVED`.

## In Progress

- None.

## Changes Requested

None.

## Planned

None.

## Blocked

- DEPLOY-001 production deployment closure is blocked until the provider
  scheduler configuration/decision is verified. Automated production
  checks now pass for Render health, CORS, OpenAPI contract, Neon connectivity,
  and Alembic version; browser Google OAuth and authenticated pool loading have
  also been verified, and the admin UI route loads after frontend redeploy.
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

Partially verified production deployment on Render + Neon.

- Backend health: `https://worldcup-porra.onrender.com/health` returned
  `{"status":"ok","database":"ok"}`.
- Frontend health: `https://worldcup-porra-p2zv.onrender.com/health` returned
  `{"status":"ok"}`.
- Frontend root returned `200` HTML.
- Backend OpenAPI returned `200` and includes `predicted_winner_team_id`,
  `/api/v1/admin/matches/{match_id}/teams`, and
  `/api/v1/admin/matches/{match_id}/status`.
- Google OAuth start redirects to Google with the production backend callback.
- CORS preflight from the frontend origin to the backend passed.
- Neon Alembic version is `20260629_0003`; production data includes 1
  tournament, 64 teams, 31 matches, 3 pools, and 2 users. The 31 matches are
  synced from the provider; 32 provider teams are loaded and 32 old seed teams
  are now unreferenced.
- Browser login with Google and authenticated pool loading were verified by
  the project owner.
- Admin UI route
  `https://worldcup-porra-p2zv.onrender.com/admin/tournaments/22c110a4-5db5-4a3d-afaa-3a098da7c3c2`
  returned `200` after frontend redeploy; project owner confirmed the sync
  screens are visible.
- Provider teams and fixtures were synced manually against Neon: `teams`
  created 32 provider teams and `matches` updated 31 matches with provider
  kickoff/team data. Result sync was not enabled because current provider
  completed-match progression conflicts with the seeded bracket links and must
  remain fail-closed until reviewed.
- Provider adapter/sync hotfix for the current provider response shape is
  approved by Reviewer after rework. Full backend checks passed with 100 tests
  and Ruff. This backend patch must be deployed before using the production
  admin sync button or an automated scheduler.
- Remaining production smoke: provider scheduler configuration/decision.

## Next Recommended Task

Redeploy backend hotfix, then decide provider results/scheduler path for
DEPLOY-001.

Rationale: Automated checks now confirm Render, Neon, migrations, OpenAPI,
health checks, CORS, authenticated pool loading, and admin UI routing. The
remaining deployment closure is operational: deploy the provider-shape hotfix,
then decide scheduled provider sync and how to handle provider result
progression conflicts.
