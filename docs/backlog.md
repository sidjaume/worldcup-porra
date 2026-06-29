# Backlog

Last updated: 2026-06-29

## PENDING_REVIEW

None.

## PLANNED

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

### BE-005: Knockout Fixture Import and Provider Sync Backend

- Owner: Backend
- Supporting agents: Architect, DevOps
- Status: DONE
- Dependencies: ARCH-003 approved contract.
- Objective: Implement backend services and repositories to import knockout fixtures, map external provider IDs, sync kickoff times/teams/results, align completed-match semantics with ARCH-003, and persist audit metadata.
- Context: Business rules remain in the Domain/Application layers. API routers must stay thin. Sync operations must be idempotent and safe to rerun.
- Relevant files: `app/domain/`, `app/services/`, `app/repositories/`, `app/models/`, `app/api/routers/tournaments.py`, `app/api/routers/admin.py`, `app/db/migrations/`, `app/providers/`, `scripts/`.
- Expected deliverables: Provider adapter interface; fixture/result sync service; external ID mapping; match audit fields; Alembic migration; sync command for knockout bracket operations; normalization for tied completed scores with explicit `winner_team_id`; import/filter path for the knockout subset from the chosen provider candidate; tests.
- Acceptance criteria: Running sync twice does not duplicate matches or points; provider status values are normalized to internal enums; kickoff changes preserve prediction-lock rules; completed matches may persist tied end-of-play scores together with an advancing winner; finished matches trigger idempotent scoring/progression; failed provider calls do not corrupt existing data.
- Required tests: Domain/service unit tests, repository integration tests, API/admin tests where endpoints change, migration smoke test.
- Documentation updates: `docs/api.md`, `docs/database.md`, `docs/environment.md`, and `docs/roadmap.md`.
- Risk: High
- Completion evidence: Added provider protocol and `WorldCup2026Adapter` normalization/filtering for knockout matches; added provider mapping/audit fields and Alembic migration; added idempotent `FixtureSyncService`; added admin kickoff correction and admin-triggered provider sync endpoints; updated scoring to use explicit advancing winner semantics for tied completed results; fixed prediction-score upsert idempotency; added CLI sync entrypoint; updated API/database/environment/roadmap docs. Follow-up review findings were fixed by making malformed provider payloads fail loudly and making provider sync phases atomic across admin and script entrypoints. Ruff passed. Backend pytest matrix passed with 53 tests, including migration, repository, provider, service, and script coverage. Independent Reviewer gate found no blocking issues for BE-005/DEVOPS-002.

### DEVOPS-002: Tournament Data Sync Operations

- Owner: DevOps
- Supporting agents: Backend
- Status: DONE
- Dependencies: ARCH-003 provider decision; BE-005 sync entrypoint.
- Objective: Define how scheduled synchronization runs in local, staging, and production environments without exposing provider credentials.
- Context: Render/Neon remain the target platform. Secrets must be environment variables only.
- Relevant files: `render.yaml`, `docker-compose.yml`, `.env.example`, `docs/deployment.md`, `docs/environment.md`, `docs/infrastructure.md`, `.github/workflows/`.
- Expected deliverables: Sync scheduling plan; environment variables for provider config; local run instructions; production runbook; logging/error handling expectations; rollback/retry guidance.
- Acceptance criteria: A developer can run sync locally; production can run scheduled sync safely; provider API keys are documented but not committed; health/observability signals expose last sync status without leaking payload secrets.
- Required tests: Config validation or smoke checks where practical; CI/build impact verified.
- Documentation updates: Deployment, environment, and infrastructure docs.
- Risk: High
- Completion evidence: Added Render cron blueprint service `worldcup-pool-fixture-sync` using the backend Docker image and documented 15-minute schedule; wired provider and sync environment variables in `render.yaml`, `.env.example`, and Docker Compose; added optional local `fixture-sync` Compose profile service; documented local run instructions, production runbook, logging/error expectations, retry guidance, manual fallback, rollback/pause steps, and MVP observability through cron logs plus match audit fields. Follow-up review findings were fixed by making the CLI `all` mode commit once only after all sync phases succeed and roll back on phase errors. Validation passed: YAML parse for `render.yaml` and `docker-compose.yml`; `docker compose --env-file .env.example --profile tools config` rendered successfully; `tests/config` passed; backend/script matrix passed with 53 tests; independent Reviewer gate found no blocking issues for BE-005/DEVOPS-002.

### ARCH-003: Knockout Data Source and Contract Decision

- Owner: Architect
- Supporting agents: Backend, DevOps, Reviewer
- Status: DONE
- Dependencies: DATA-EPIC-001 architecture/planning clarification
- Objective: Select the production approach for tournament data ingestion and document the contract boundaries.
- Context: Accepted in ADR form as a hybrid model: official/manual bracket seed, approved provider-assisted operational updates, and admin fallback. Scraping is explicitly rejected as the primary production dependency.
- Relevant files: `docs/architecture.md`, `docs/api.md`, `docs/database.md`, `docs/roadmap.md`, `docs/decisions/`.
- Expected deliverables: ADR for data source strategy; canonical internal match/team/result semantics; provider abstraction contract; explicit scoring rule for penalty-decided matches.
- Acceptance criteria: Trade-offs are documented; selected approach respects modular monolith boundaries; frontend/backend API impact is clear; follow-up tasks are unblocked.
- Required tests: None for decision-only work.
- Documentation updates: Architecture, API/database notes, roadmap, and a new ADR if the selected provider or abstraction has long-term impact.
- Risk: High
- Completion evidence: Reviewer approved ARCH-003 with comments. Added [ARCH-003 ADR](./decisions/arch-003-knockout-data-source-and-result-contract.md) as an accepted decision record. The decision uses a hybrid seed-plus-provider-plus-admin model, defines scoring semantics as end-of-play goals plus explicit advancing winner, excludes penalty shoot-out goals from exact-score evaluation, and evaluates `rezarahiminia/worldcup2026` as the preferred initial free provider candidate through import/self-hosting rather than blind dependency on its public host.

### ORCH-001: Architecture and Contract Reconciliation

- Owner: Architect
- Supporting agents: None for first pass
- Status: DONE
- Dependencies: Current repository status inspection
- Acceptance criteria: `docs/architecture.md`, `docs/api.md`, `docs/database.md`, and `docs/roadmap.md` accurately reflect the current implementation status; unresolved contract gaps are documented as follow-up tasks; no specialist implementation is bundled into the reconciliation.
- Risk: Medium
- Completion evidence: Reviewer approved ORCH-001 with comments. Corrected `POST /api/v1/pools` contract reconciliation after Reviewer finding. `docs/api.md`, frontend `CreatePoolResponse`, and OpenAPI `PoolCreated` now include `participant_count` and `created_at`. Added OpenAPI contract coverage. Backend contract test passed, full backend tests passed with 41 tests, focused frontend tests passed, and frontend typecheck passed with documented `npm.cmd` invocation.

### BE-006: Pool Active-State Contract and Authorization Fix

- Owner: Backend
- Supporting agents: Architect, Frontend, Reviewer
- Status: DONE
- Dependencies: REV-002 findings
- Acceptance criteria: Pool detail responses expose the active state or the contract is intentionally revised; inactive pools are not treated as usable member pools unless explicitly allowed by a documented rule; frontend types and UI do not guess missing active state; affected backend/frontend tests are updated.
- Risk: Medium
- Completion evidence: Reviewer approved BE-006. Removed the pool active toggle from `PoolSettingsForm` until an inactive-pool management view exists, and changed `updatePoolAction` to update only the pool name from that form. This prevents owners from deactivating a pool through the normal detail page and losing the UI path back. Frontend lint passed; focused frontend tests passed; frontend typecheck passed with documented `npm.cmd` invocation; backend Ruff passed; backend tests passed with 41 tests.

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

### FE-007: Pool Creation Invite-Code and Owner-Control UX Fix

- Owner: Frontend
- Supporting agents: Backend, Product Designer, Reviewer
- Dependencies: REV-002 findings; existing pool create/rotate invite API contract.
- Acceptance criteria: After pool creation, the owner can immediately view/copy the initial invite code without rotating it; non-owners do not see misleading owner-only controls; backend remains the authorization source of truth; loading/error/success feedback remains accessible.
- Status: DONE
- Risk: Medium
- Completion evidence: Reviewer approved FE-007 with comments. `createPoolAction` returns the created pool id and initial invite code; `CreatePoolForm` displays the initial invite code with copy feedback and an `Open pool` link; invite-code copy UI is shared with rotation; pool detail hides invite-code rotation and pool settings for non-owners. Frontend lint, tests, typecheck, and build passed using the documented Windows `npm.cmd` invocation.

### DEVOPS-003: CI Coverage for DB and Repository Integration Tests

- Owner: DevOps
- Supporting agents: Backend, Reviewer
- Status: DONE
- Dependencies: REV-002 findings; BE-001 integration tests.
- Objective: Ensure CI runs the migration and repository integration tests that were added for BE-001.
- Context: REV-002 found that `.github/workflows/ci.yml` ran only `tests/api tests/domain tests/services`, leaving `tests/db` and `tests/repositories` out of CI.
- Relevant files: `.github/workflows/ci.yml`, `tests/conftest.py`, `tests/db/`, `tests/repositories/`.
- Acceptance criteria: CI provisions or otherwise targets a PostgreSQL test database for integration tests, runs `tests/db` and `tests/repositories`, and still skips safely only when intentionally configured outside CI.
- Required tests: CI workflow validation plus local command evidence for the updated backend test matrix where practical.
- Documentation updates: `docs/infrastructure.md`.
- Risk: Medium
- Completion evidence: Reviewer approved DEVOPS-003. Backend CI now provisions a PostgreSQL 16 service with a non-secret test database URL, sets `ENVIRONMENT=test`, and runs `tests/api tests/config tests/domain tests/services tests/db tests/repositories` so migration smoke tests and repository integration tests are included. Local Ruff, compileall, workflow YAML parse, and the updated backend pytest matrix passed; pytest reported 41 passed.

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
- Status: DONE
- Risk: Medium
- Completion evidence: Reviewer decision was `CHANGES_REQUESTED`. Major findings were split into BE-006, FE-007, and DEVOPS-003; minor documentation cleanup was split into DOCS-002. Follow-up implementations were later approved, and the closure review was rerun so the parent record can be closed coherently.

### REV-001: Independent Production-Readiness Review

- Owner: Reviewer
- Supporting agents: Architect
- Dependencies: ORCH-001 preferred first, but review can begin from current diffs
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES_REQUESTED`; findings are classified by severity with file references and required follow-up owners.
- Status: CHANGES_REQUESTED
- Risk: Medium

## PLANNED_EPICS

### DATA-EPIC-001: World Cup 2026 Knockout Data Operations

- Owner: Orchestrator
- Supporting agents: Architect, Backend, DevOps, Product Designer, Frontend, Reviewer
- Status: PLANNED
- Dependencies: ARCH-003 approved.
- Objective: Define and implement a reliable way to load the FIFA World Cup 2026 knockout bracket, keep kickoff times/results updated, lock predictions safely, score finished matches, and provide manual admin fallback.
- Scope: Round of 32, Round of 16, quarter-finals, semi-finals, final. Third-place match remains out of MVP scope unless explicitly added.
- Out of scope: Group-stage management, qualification calculations, league standings, and scraping as a primary production data source.
- Architecture decision: Use the hybrid model from [ARCH-003 ADR](./decisions/arch-003-knockout-data-source-and-result-contract.md): official/manual bracket seed, one approved provider adapter for operational updates, and admin fallback with auditable overrides. The preferred initial free candidate is `rezarahiminia/worldcup2026`, consumed through import/self-hosting or a controlled adapter rather than as a sole third-party uptime dependency.
- Canonical result semantics: completed knockout matches are scored from end-of-play goals, while `winner_team_id` represents the advancing team; penalty shoot-out goals do not count toward exact-score or team-goal bonuses.
- Next executable sequence: `UX-002` admin correction flow, `FE-006` admin UI, then `REV-003`.
- Acceptance criteria: The app can initialize knockout fixtures, sync teams/times/results from an approved source, audit changes, handle provider failure through admin fallback, and recalculate scoring idempotently after finished matches.
- Risk: High

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
