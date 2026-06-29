# Backlog

Last updated: 2026-06-29

## PENDING_REVIEW

### ORCH-001: Architecture and Contract Reconciliation

- Owner: Architect
- Supporting agents: None for first pass
- Status: PENDING_REVIEW
- Dependencies: Current repository status inspection
- Acceptance criteria: `docs/architecture.md`, `docs/api.md`, `docs/database.md`, and `docs/roadmap.md` accurately reflect the current implementation status; unresolved contract gaps are documented as follow-up tasks; no specialist implementation is bundled into the reconciliation.
- Risk: Medium

### BE-006: Pool Active-State Contract and Authorization Fix

- Owner: Backend
- Supporting agents: Architect, Frontend, Reviewer
- Status: PENDING_REVIEW
- Dependencies: REV-002 findings
- Acceptance criteria: Pool detail responses expose the active state or the contract is intentionally revised; inactive pools are not treated as usable member pools unless explicitly allowed by a documented rule; frontend types and UI do not guess missing active state; affected backend/frontend tests are updated.
- Risk: Medium
- Completion evidence: Implementation is complete. `PoolDetail` now includes `is_active`; normal member access rejects inactive pools; owner update can reactivate inactive pools; frontend `PoolDetail.is_active` is required and `PoolSettingsForm` uses the explicit value. Backend Ruff passed and `.venv\Scripts\python.exe -m pytest tests -q` passed with 40 tests. Frontend checks are still pending because `node` and `npm` are unavailable in this shell.

### FE-007: Pool Creation Invite-Code and Owner-Control UX Fix

- Owner: Frontend
- Supporting agents: Backend, Product Designer, Reviewer
- Status: PENDING_REVIEW
- Dependencies: REV-002 findings; existing pool create/rotate invite API contract.
- Objective: Ensure a newly created pool owner can see and copy the initial invite code, and hide or disable owner-only controls for non-owners.
- Context: REV-002 found that `createPoolAction` redirects using only `pool.id`, so the initial invite code returned by the backend is lost. It also found owner-only pool controls render for all members even though backend authorization blocks non-owners.
- Relevant files: `frontend/app/actions.ts`, `frontend/app/pools/[poolId]/page.tsx`, `frontend/components/pools/InviteCodeForm.tsx`, `frontend/components/pools/PoolSettingsForm.tsx`, `frontend/components/pools/ParticipantList.tsx`, `frontend/types/api.ts`.
- Acceptance criteria: After pool creation, the owner can immediately view/copy the initial invite code without rotating it; non-owners do not see misleading owner-only controls; backend remains the authorization source of truth; loading/error/success feedback remains accessible.
- Required tests: Frontend action/component tests for create-pool invite-code handling and role-based owner controls.
- Documentation updates: `docs/frontend.md` if the user flow changes materially.
- Risk: Medium
- Completion evidence: Implementation is complete. `createPoolAction` returns the created pool id and initial invite code; `CreatePoolForm` displays the initial invite code with copy feedback and an `Open pool` link; invite-code copy UI is shared with rotation; pool detail hides invite-code rotation and pool settings for non-owners. Backend checks passed; frontend checks are still pending because `node` and `npm` are unavailable in this shell.

## CHANGES_REQUESTED

### DEVOPS-003: CI Coverage for DB and Repository Integration Tests

- Owner: DevOps
- Supporting agents: Backend, Reviewer
- Status: CHANGES_REQUESTED
- Dependencies: REV-002 findings; BE-001 integration tests.
- Objective: Ensure CI runs the migration and repository integration tests that were added for BE-001.
- Context: REV-002 found that `.github/workflows/ci.yml` runs only `tests/api tests/domain tests/services`, leaving `tests/db` and `tests/repositories` out of CI.
- Relevant files: `.github/workflows/ci.yml`, `tests/conftest.py`, `tests/db/`, `tests/repositories/`.
- Acceptance criteria: CI provisions or otherwise targets a PostgreSQL test database for integration tests, runs `tests/db` and `tests/repositories`, and still skips safely only when intentionally configured outside CI.
- Required tests: CI workflow validation plus local command evidence for the updated backend test matrix where practical.
- Documentation updates: `docs/infrastructure.md` or `docs/deployment.md` if CI setup requirements change.
- Risk: Medium

## PLANNED

### DATA-EPIC-001: World Cup 2026 Knockout Data Operations

- Owner: Orchestrator
- Supporting agents: Architect, Backend, DevOps, Product Designer, Frontend, Reviewer
- Status: PLANNED
- Dependencies: REV-002 changes resolved; product decision on data provider budget and licensing.
- Objective: Define and implement a reliable way to load the FIFA World Cup 2026 knockout bracket, keep kickoff times/results updated, lock predictions safely, score finished matches, and provide manual admin fallback.
- Scope: Round of 32, Round of 16, quarter-finals, semi-finals, final. Third-place match remains out of MVP scope unless explicitly added.
- Out of scope: Group-stage management, qualification calculations, league standings, and scraping as a primary production data source.
- Acceptance criteria: The app can initialize knockout fixtures, sync teams/times/results from an approved source, audit changes, handle provider failure through admin fallback, and recalculate scoring idempotently after finished matches.
- Risk: High

### ARCH-003: Knockout Data Source and Contract Decision

- Owner: Architect
- Supporting agents: Backend, DevOps, Reviewer
- Status: PLANNED
- Dependencies: DATA-EPIC-001; provider options and cost/licensing constraints from the user or project owner.
- Objective: Select the production approach for tournament data ingestion and document the contract boundaries.
- Context: Recommended strategy is a hybrid model: official/manual schedule seed, paid or approved sports data provider for results and time changes, and admin fallback. Scraping should not be the primary production dependency.
- Relevant files: `docs/architecture.md`, `docs/api.md`, `docs/database.md`, `docs/roadmap.md`, `docs/decisions/`.
- Expected deliverables: ADR for data source strategy; canonical internal match/team/result status model; provider abstraction contract; decision on whether exact-score predictions use 90-minute score, extra-time score, or final score excluding penalties.
- Acceptance criteria: Trade-offs are documented; selected approach respects modular monolith boundaries; frontend/backend API impact is clear; follow-up tasks are unblocked.
- Required tests: None for decision-only work.
- Documentation updates: Architecture, API/database notes, roadmap, and a new ADR if the selected provider or abstraction has long-term impact.
- Risk: High

### BE-005: Knockout Fixture Import and Provider Sync Backend

- Owner: Backend
- Supporting agents: Architect, DevOps
- Status: PLANNED
- Dependencies: ARCH-003 approved contract.
- Objective: Implement backend services and repositories to import knockout fixtures, map external provider IDs, sync kickoff times/teams/results, and persist audit metadata.
- Context: Business rules remain in the Domain/Application layers. API routers must stay thin. Sync operations must be idempotent and safe to rerun.
- Relevant files: `app/domain/`, `app/services/`, `app/repositories/`, `app/models/`, `app/api/routers/tournaments.py`, `app/api/routers/admin.py`, `app/db/migrations/`, `scripts/`.
- Expected deliverables: Provider adapter interface; fixture/result sync service; external ID mapping; match audit fields or table; Alembic migration; seed/update command for knockout bracket; tests.
- Acceptance criteria: Running sync twice does not duplicate matches or points; provider status values are normalized to internal enums; kickoff changes preserve prediction-lock rules; finished matches trigger idempotent scoring/progression; failed provider calls do not corrupt existing data.
- Required tests: Domain/service unit tests, repository integration tests, API/admin tests where endpoints change, migration smoke test.
- Documentation updates: `docs/api.md`, `docs/database.md`, and `docs/roadmap.md`.
- Risk: High

### DEVOPS-002: Tournament Data Sync Operations

- Owner: DevOps
- Supporting agents: Backend
- Status: PLANNED
- Dependencies: ARCH-003 provider decision; BE-005 sync entrypoint.
- Objective: Define how scheduled synchronization runs in local, staging, and production environments without exposing provider credentials.
- Context: Render/Neon remain the target platform. Secrets must be environment variables only.
- Relevant files: `render.yaml`, `docker-compose.yml`, `.env.example`, `docs/deployment.md`, `docs/environment.md`, `docs/infrastructure.md`, `.github/workflows/`.
- Expected deliverables: Sync scheduling plan; environment variables for provider config; local run instructions; production runbook; logging/error handling expectations; rollback/retry guidance.
- Acceptance criteria: A developer can run sync locally; production can run scheduled sync safely; provider API keys are documented but not committed; health/observability signals expose last sync status without leaking payload secrets.
- Required tests: Config validation or smoke checks where practical; CI/build impact verified.
- Documentation updates: Deployment, environment, and infrastructure docs.
- Risk: High

### UX-002: Admin Data Correction and Sync Visibility Flow

- Owner: Product Designer
- Supporting agents: Frontend, Backend
- Status: PLANNED
- Dependencies: ARCH-003 internal data/status model; BE-005 admin API shape.
- Objective: Specify the minimal admin experience for viewing sync status and correcting teams, kickoff times, match status, and final results.
- Context: The fallback UI is operationally critical during the tournament. It should be fast, clear, and hard to misuse.
- Relevant files: `docs/frontend.md`, `frontend/app/`, `frontend/components/`.
- Expected deliverables: Admin user flow; screen/content specification; error/confirmation states; accessibility requirements; API data needs for frontend.
- Acceptance criteria: Admins can identify stale/failed syncs, manually correct a match, confirm result changes, and understand whether scoring was recalculated.
- Required tests: None for design-only work; implementation tasks will require component/route tests.
- Documentation updates: Frontend docs or backlog implementation tasks.
- Risk: Medium

### FE-006: Admin Match Data Management UI

- Owner: Frontend
- Supporting agents: Product Designer, Backend
- Status: PLANNED
- Dependencies: UX-002 approved flow; BE-005 admin API contract.
- Objective: Implement the admin UI for sync visibility and manual match corrections.
- Context: Frontend must consume documented backend endpoints and must not duplicate scoring, progression, or provider normalization rules.
- Relevant files: `frontend/app/`, `frontend/components/`, `frontend/lib/api/`, `frontend/types/`.
- Expected deliverables: Admin match list/detail UI; sync status display; result/time/team correction forms; confirmation states; loading/error states; tests.
- Acceptance criteria: Authorized admins can correct match data from the UI; unauthorized users cannot access admin controls; UI is responsive and accessible; actions show clear success/failure feedback.
- Required tests: Component/route tests for rendering, form behavior, and API client integration boundaries.
- Documentation updates: `docs/frontend.md` and `docs/api.md` if frontend-facing contract examples are added.
- Risk: Medium

### REV-003: Knockout Data Operations Review

- Owner: Reviewer
- Supporting agents: Architect, Backend, DevOps, Frontend
- Status: PLANNED
- Dependencies: ARCH-003, BE-005, DEVOPS-002, UX-002, and FE-006 completed or ready for review.
- Objective: Review the full tournament data operations slice for correctness, security, maintainability, and tournament-day readiness.
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES_REQUESTED`; findings are classified by severity; provider failure, manual fallback, scoring idempotency, and prediction locking are explicitly checked.
- Required tests: Reviewer confirms relevant backend, frontend, migration, and deployment checks were run.
- Documentation updates: Backlog and project status updated with review outcome.
- Risk: High

## DONE

### FE-002: Mobile Navigation and Page Context

- Owner: Frontend
- Supporting agents: Product Designer, Reviewer
- Dependencies: UX-001 findings
- Acceptance criteria: Mobile users can navigate primary app sections; active navigation uses visible state and `aria-current`; pool detail, predictions, and rankings keep clear pool context and subnavigation.
- Status: DONE
- Risk: Medium
- Completion evidence: Added primary mobile navigation/current-page state, pool subnavigation, and focused navigation tests.

### FE-003: Mobile-Safe Rankings and Participants

- Owner: Frontend
- Supporting agents: Product Designer, Reviewer
- Dependencies: UX-001 findings
- Acceptance criteria: Rankings and participant lists work on narrow screens without clipping; layout is either horizontally scrollable with clear affordance or responsive card-based; ranking labels are understandable.
- Status: DONE
- Risk: Medium
- Completion evidence: Rankings and participants now render mobile card layouts with clearer metric labels and focused tests.

### FE-004: Accessibility Interaction Pass

- Owner: Frontend
- Supporting agents: Product Designer, Reviewer
- Dependencies: UX-001 findings
- Acceptance criteria: Buttons, links, tabs, and form controls have visible `focus-visible` states; form errors/success messages are announced and associated with controls; color tokens meet WCAG AA for normal text.
- Status: DONE
- Risk: Medium
- Completion evidence: Shared focus-visible styles, darker contrast tokens, stage/nav active states, and announced/associated form feedback added.

### FE-005: Prediction and Invite-Code UX Hardening

- Owner: Frontend
- Supporting agents: Product Designer, Reviewer
- Dependencies: UX-001 findings
- Acceptance criteria: Prediction inputs are labeled with actual team names and respect documented prediction status; route-level loading/error states exist for major pages; invite-code rotation has safer confirmation/copy affordance.
- Status: DONE
- Risk: Medium
- Completion evidence: Prediction form labels now use team names, non-editable prediction statuses are read-only, route loading/error states were added, and invite-code rotation now requires confirmation and supports copy.

### DEVOPS-001: Environment and OAuth Configuration Audit

- Owner: DevOps
- Supporting agents: Backend
- Dependencies: Architect confirmation of backend-owned OAuth callback contract
- Acceptance criteria: `.env.example`, docs, `docker-compose.yml`, Render variables, and settings defaults agree on backend/frontend callback URLs and frontend origins; no secrets are exposed; local and production setup instructions are consistent.
- Status: DONE
- Risk: Medium

### BE-001: Repository and Migration Integration Coverage

- Owner: Backend
- Supporting agents: DevOps
- Dependencies: Local PostgreSQL or CI service database availability
- Acceptance criteria: Migration smoke test and repository integration tests cover schema recreation, key constraints, pool membership, prediction upsert, and ranking query behavior.
- Status: DONE
- Risk: Medium

### BE-002: API Contract Alignment for Pool Endpoint

- Owner: Backend
- Supporting agents: Architect, Frontend
- Dependencies: ORCH-001 findings and API contract decision
- Acceptance criteria: `PATCH /api/v1/pools/{pool_id}` response shape is either implemented to match `docs/api.md` or `docs/api.md` is intentionally narrowed with frontend types updated; affected tests are added or updated.
- Status: DONE
- Risk: Medium

### BE-003: Ranking Tie-Breaker Contract Alignment

- Owner: Backend
- Supporting agents: Architect
- Dependencies: Architect decision on final deterministic tie-breaker
- Acceptance criteria: Ranking implementation, `docs/api.md`, `docs/database.md`, and tests agree on tie-breakers after total points, exact scores, and correct winners.
- Status: DONE
- Risk: Low

### BE-004: API Error Format Standardization Review

- Owner: Backend
- Supporting agents: Reviewer
- Dependencies: REV-001 findings
- Acceptance criteria: Expected service/domain/auth errors and request validation errors either all use the standard `{ "error": { "code", "message", "details" } }` body, or accepted exceptions are documented in `docs/api.md`.
- Status: DONE
- Risk: Low

### DOCS-002: Roadmap Review-Gate Status Cleanup

- Owner: Orchestrator
- Supporting agents: Architect, Reviewer
- Dependencies: REV-002 findings
- Acceptance criteria: Roadmap gate status matches current backlog/project-status records; no completed audit is described as pending.
- Status: DONE
- Risk: Low
- Completion evidence: Updated roadmap gate status to record REV-002 changes requested and DEVOPS-001 OAuth/environment audit completion.

## COMPLETED_REVIEW

### UX-001: Product Designer Usability and Accessibility Pass

- Owner: Product Designer
- Supporting agents: Frontend, Reviewer
- Dependencies: Current Next.js screens
- Acceptance criteria: Critical user flows are reviewed for mobile layout, focus states, labels, contrast, loading, empty, and error states; findings are converted into frontend tasks.
- Status: CHANGES_REQUESTED
- Risk: Medium
- Findings: Mobile navigation/current-page context, mobile rankings/participants, focus-visible states, prediction input labeling/status handling, route-level loading/error states, announced form feedback, color contrast, invite-code rotation safety, and rankings label clarity need frontend follow-up.

### REV-002: Focused Production-Readiness Re-review

- Owner: Reviewer
- Supporting agents: Architect
- Dependencies: DONE technical fixes and UX findings converted into frontend tasks
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES_REQUESTED`; findings are classified by severity with file references and required follow-up owners.
- Status: CHANGES_REQUESTED
- Risk: Medium
- Completion evidence: Reviewer decision was `CHANGES_REQUESTED`. Major findings were split into BE-006, FE-007, and DEVOPS-003; minor documentation cleanup was split into DOCS-002.

### REV-001: Independent Production-Readiness Review

- Owner: Reviewer
- Supporting agents: Architect
- Dependencies: ORCH-001 preferred first, but review can begin from current diffs
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES_REQUESTED`; findings are classified by severity with file references and required follow-up owners.
- Status: CHANGES_REQUESTED
- Risk: Medium

## BLOCKED

### DEPLOY-001: Production Render + Neon Deployment

- Owner: DevOps
- Supporting agents: Backend, Frontend
- Blocker: Requires external Render account, Neon database, Google OAuth client, and production secrets.
- Acceptance criteria: Render services deploy successfully, migrations run against Neon, health checks pass, and OAuth smoke test succeeds.
- Risk: High

## DEFERRED

### HARDEN-001: Rate Limiting and Abuse Protection

- Owner: Backend
- Supporting agents: Architect, DevOps, Reviewer
- Dependencies: MVP flow stabilization
- Acceptance criteria: Auth and invite-code endpoints have appropriate rate limiting or abuse mitigation.
- Risk: Medium
