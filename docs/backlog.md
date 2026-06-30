# Backlog

Last updated: 2026-06-30

## PENDING_REVIEW

None.

## PLANNED

None.

## DONE

### DEVOPS-005: Free-Plan Render Blueprint Cron Cleanup

- Owner: DevOps
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: REV-003 re-review.
- Objective: Ensure the Render blueprint used for the current free-plan path does not provision or imply reliance on an unsupported Render cron service.
- Acceptance criteria: `render.yaml` defines only the backend and frontend web services for the current free-plan default blueprint; deployment/infrastructure/environment docs describe local/operator scheduled sync against Neon as the active free-plan path; optional Render cron guidance remains clearly plan-dependent and cannot be accidentally provisioned by the default blueprint.
- Required tests: YAML parse for `render.yaml`; docs consistency grep for Render cron/free-plan guidance.
- Documentation updates: `docs/deployment.md`, `docs/infrastructure.md`, `docs/project-status.md`, and `docs/backlog.md`.
- Risk: Low
- Completion evidence: Removed the `worldcup-pool-fixture-sync` `type: cron`
  service from `render.yaml`, leaving only backend and frontend web services in
  the default blueprint. Updated deployment and infrastructure docs so
  local/operator scheduled sync against Neon is the active free-plan path and
  Render cron is only a future paid/eligible-plan option to add intentionally.
  YAML parse and docs consistency grep passed. Independent Reviewer gate
  decision: `APPROVED`.

### REV-003: Knockout Data Operations Review

- Owner: Reviewer
- Supporting agents: Architect, Backend, DevOps, Frontend
- Status: DONE
- Dependencies: ARCH-003, ARCH-004, BE-005, DEVOPS-002, UX-002,
  FE-006, BE-007, BE-008, BE-009, BE-010, DEVOPS-004, FE-008, and
  FE-009 completed or ready for review.
- Objective: Review the full tournament data operations slice for correctness, security, maintainability, and tournament-day readiness.
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES_REQUESTED`; findings are classified by severity; provider failure, manual fallback, scoring idempotency, and prediction locking are explicitly checked.
- Required tests: Reviewer confirms relevant backend, frontend, migration, and deployment checks were run.
- Documentation updates: Backlog and project status updated with review outcome.
- Risk: High
- Completion evidence: Independent Reviewer re-review decision:
  `APPROVED WITH COMMENTS`. All prior REV-003 findings are remediated:
  provider/manual override protection, tied-score advancing-winner predictions,
  admin team/status fallback, provider fail-closed normalization with zero-score
  preservation, free-plan sync documentation, and frontend `locked`/
  `in_progress` status handling. Reviewer ran focused backend checks with 61
  tests and Ruff; Orchestrator evidence included full backend tests (91
  passed), backend Ruff, full frontend tests (44 passed), frontend lint, and
  frontend typecheck. Non-blocking follow-up: `DEVOPS-005` should ensure the
  default Render blueprint cannot accidentally provision the optional cron
  service on the free-plan path.

### FE-009: Tied Prediction and Admin Correction UI Alignment

- Owner: Frontend
- Supporting agents: Backend, Reviewer
- Status: DONE
- Dependencies: BE-008 and BE-009.
- Objective: Update frontend prediction and admin operations UI for the ARCH-004 prediction/admin correction contract.
- Acceptance criteria: Tied-score prediction forms require an advancing-winner selection and send `predicted_winner_team_id`; non-tied predictions omit/null the field; existing-match team and status corrections call the documented admin endpoints; frontend shows backend validation errors without duplicating scoring or provider rules.
- Required tests: Frontend API/type/component tests for tied predictions, team correction, status correction, and error states.
- Documentation updates: `docs/frontend.md`.
- Risk: Medium
- Completion evidence: Prediction write types/API/actions now carry
  `predicted_winner_team_id`; tied prediction forms show a required
  advancing-winner selector, while non-tied submissions clear the field to
  `null`. Admin operations now expose existing-match team and operational
  status corrections wired to the documented `/teams` and `/status`
  endpoints, with completed status still handled by result completion.
  Focused frontend tests passed with 26 tests; full frontend tests passed with
  44 tests; lint passed; typecheck passed after elevated rerun because
  sandboxed Next type generation hit `EPERM` writing `.next/types/routes.d.ts`.
  Independent Reviewer gate decision: `APPROVED WITH COMMENTS`; non-blocking
  comment noted some tests use source-text assertions, consistent with current
  repo style.

### FE-008: Match Status Contract Alignment

- Owner: Frontend
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: Backend `MatchStatus` contract.
- Objective: Align frontend match status typing and admin filters with backend `locked` and `in_progress` statuses.
- Acceptance criteria: Frontend `MatchStatus` type covers backend statuses; admin filters and display handle locked/in-progress states; tests cover the added statuses.
- Required tests: Frontend type/API/component tests.
- Documentation updates: `docs/frontend.md` already documents the status handling contract.
- Risk: Low
- Completion evidence: Added `locked` and `in_progress` to frontend `MatchStatus`; admin status filters and display labels now cover all backend statuses; prediction cards keep locked and in-progress matches read-only with explicit copy. Focused frontend tests, full frontend tests, lint, and typecheck passed. Independent Reviewer gate decision: `APPROVED WITH COMMENTS`; non-blocking comment noted some status coverage uses source-text assertions, consistent with current repo style.

### DEVOPS-004: Free-Plan Sync Operations Runbook

- Owner: DevOps
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: User decision to avoid paid Render cron; ARCH-004 free-plan
  sync contract accepted.
- Objective: Update operations docs so production sync does not assume Render
  cron on the current free-plan deployment path.
- Acceptance criteria: Render cron is clearly documented as optional/plan-dependent; local scheduled sync against Neon is documented with Windows Task Scheduler or equivalent; secrets handling and tournament UUID setup are explicit; status docs no longer overstate Render cron availability.
- Required tests: Documentation review; command syntax sanity where practical.
- Documentation updates: `docs/deployment.md`, `docs/infrastructure.md`, `docs/environment.md`, `docs/project-status.md`, `docs/backlog.md`.
- Risk: Medium
- Completion evidence: Free-plan local/operator scheduled sync against Neon is documented as the MVP path, with Render cron retained only as optional and plan-dependent. Windows Task Scheduler and Linux/macOS equivalent commands, required environment variables, production tournament UUID setup, safe secret handling, logs, retry, and disable guidance were added. YAML parse, sync CLI help, docs consistency grep, and scoped diff check passed. Independent Reviewer gate decision: `APPROVED`.

### BE-010: Provider Normalization Fail-Closed Hardening

- Owner: Backend
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: ARCH-004 provider normalization contract.
- Objective: Make provider status/score normalization fail closed on unknown statuses and preserve legitimate zero scores in nested score payloads.
- Acceptance criteria: Unknown provider statuses produce provider/sync errors and do not mutate match state; completed provider rows with missing scores or winner fail closed; numeric zero scores are parsed and preserved from nested payloads; tests cover unknown status, 0-0, and one-sided zero score cases.
- Required tests: Provider adapter tests and affected sync service tests.
- Documentation updates: Status/evidence only; ARCH-004 contract remains unchanged.
- Risk: High
- Completion evidence: Backend implemented fail-closed provider status parsing, completed-result winner/score validation, and nested zero-score preservation. Focused checks passed with 18 tests and focused Ruff; full checks passed with 91 tests and `.\.venv\Scripts\python.exe -m ruff check .`. Independent Reviewer gate decision: `APPROVED`.

### BE-007: Provider Sync Manual Override Protection

- Owner: Backend
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: ARCH-004; BE-009.
- Objective: Prevent provider sync/result progression from silently overwriting downstream bracket slots affected by manual corrections.
- Acceptance criteria: Provider sync skips provider-managed writes for matches with `admin_override=true`; admin result correction marks downstream matches as manually overridden when it changes a propagated slot; provider progression fills only empty or same-team downstream slots; conflicts are reported as sync errors instead of overwriting; regression tests cover downstream overwrite scenarios.
- Required tests: Fixture sync/admin service regression tests.
- Completion evidence: Admin completion now marks changed downstream propagated slots with `sync_source="admin"` and `admin_override=true`; provider progression now skips downstream manual overrides, allows empty/same-team slots, and reports conflicts without overwrite. Focused service tests passed with 27 tests; full backend tests passed with 84 tests; Ruff passed. Independent Reviewer gate decision: `APPROVED`.
- Risk: High

### BE-009: Admin Team and Status Correction Fallback

- Owner: Backend
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: ARCH-004 admin correction contract.
- Objective: Provide safe admin fallback for correcting existing-match teams and operational status when provider data is wrong.
- Acceptance criteria: `PATCH /api/v1/admin/matches/{match_id}/teams` corrects non-completed match teams or unresolved slots and sets `sync_source=admin`/`admin_override=true`; `PATCH /api/v1/admin/matches/{match_id}/status` accepts only `scheduled`, `locked`, `in_progress`, and `cancelled` for non-completed matches and sets manual override fields; neither endpoint scores predictions, completes matches, reopens completed matches, or edits bracket linkage; frontend can consume documented endpoints without inventing behavior.
- Completion evidence: Added admin request schemas, route handlers, `AdminService` team/status correction commands, service validation tests, and OpenAPI contract tests. Focused backend checks passed with `.\.venv\Scripts\python.exe -m pytest tests/services/test_admin_service.py tests/api/test_api_contract.py` and focused Ruff. Full backend checks passed with `.\.venv\Scripts\python.exe -m pytest` (79 passed) and `.\.venv\Scripts\python.exe -m ruff check .`. Independent Reviewer gate decision: `APPROVED`.
- Risk: High

### BE-008: Tied Prediction Advancing-Winner Semantics

- Owner: Backend
- Supporting agents: Reviewer
- Status: DONE
- Dependencies: ARCH-004 prediction contract.
- Objective: Allow predictions for tied end-of-play knockout scores to express the predicted advancing winner, so ADR scoring semantics can be applied.
- Acceptance criteria: `predicted_winner_team_id` is persisted and exposed by prediction APIs; tied predictions require a home/away advancing team; non-tied predictions omit/null the field and derive winner from goals; tied predictions are rejected while teams are unknown; scoring awards correct-winner points according to the documented predicted winner; API, database, and backend tests agree. Frontend type/UI alignment remains tracked in FE-009.
- Required tests: Domain scoring tests, prediction service/API tests, migration smoke tests, frontend API/type tests when FE-009 updates the UI contract.
- Documentation updates: `docs/api.md`, `docs/database.md`, `docs/frontend.md`.
- Risk: High
- Completion evidence: Added migration `20260629_0003`, backend model/schema/repository/service/scoring support, and focused tests for tied home/away advancing winners, missing/invalid winner validation, non-tied winner rejection, scoring, API schema exposure, repository persistence, and migration shape. Backend checks passed: `.\.venv\Scripts\python.exe -m pytest` (63 passed) and `.\.venv\Scripts\python.exe -m ruff check .`. Independent Reviewer gate decision: `APPROVED WITH COMMENTS`; non-blocking comment noted that frontend prediction response/write types still need `predicted_winner_team_id`, already covered by FE-009.

### ARCH-004: Knockout Operations Remediation Contract

- Owner: Architect
- Supporting agents: Backend, Frontend, DevOps, Reviewer
- Status: DONE
- Dependencies: REV-003 findings.
- Objective: Define the minimal contract changes required to resolve REV-003 findings around tied predictions, manual fallback coverage, provider/manual override boundaries, provider fail-closed behavior, and free-plan sync operations.
- Context: REV-003 found that the implemented operations slice does not yet fully satisfy ARCH-003 tournament-day semantics and fallback requirements.
- Relevant files: `docs/decisions/`, `docs/api.md`, `docs/database.md`, `docs/frontend.md`, `docs/deployment.md`, `docs/infrastructure.md`, `docs/environment.md`, `docs/backlog.md`, `docs/project-status.md`.
- Expected deliverables: Accepted ADR and synchronized contract notes specifying prediction advancing-winner semantics, admin team/status correction scope, provider overwrite protection rules, fail-closed provider normalization, free-plan sync operations, and follow-up implementation tasks.
- Acceptance criteria: Backend/frontend/API/database impacts are explicit; implementation tasks can proceed without inventing contracts; MVP scope remains as small as safely possible.
- Required tests: None for decision-only work.
- Documentation updates: Added [ARCH-004 ADR](./decisions/arch-004-knockout-operations-remediation-contract.md) and synchronized API, database, frontend, deployment, infrastructure, environment, backlog, and project-status notes.
- Risk: High
- Completion evidence: Decided `predicted_winner_team_id` is required only for tied predictions; added narrow admin team/status correction endpoints; preserved match-level manual override protection for provider sync and downstream bracket slots; required provider normalization to fail closed for unknown statuses/missing completed data while preserving zero scores; documented Render cron as optional with local scheduled sync against Neon as the free-plan path; refined remediation task sequencing and acceptance criteria.

### FE-006: Admin Match Data Management UI

- Owner: Frontend
- Supporting agents: Product Designer, Backend
- Status: DONE
- Dependencies: UX-002 completed flow; BE-005 admin API contract.
- Objective: Implement the admin UI for sync visibility and manual match corrections.
- Context: Frontend must consume documented backend endpoints and must not duplicate scoring, progression, or provider normalization rules.
- Relevant files: `frontend/app/`, `frontend/components/`, `frontend/lib/api/`, `frontend/types/`.
- Expected deliverables: Admin match list/detail UI; sync status display; result/time/team correction forms; confirmation states; loading/error states; tests.
- Acceptance criteria: Authorized admins can correct match data from the UI; unauthorized users cannot access admin controls; UI is responsive and accessible; actions show clear success/failure feedback.
- Required tests: Component/route tests for rendering, form behavior, and API client integration boundaries.
- Documentation updates: `docs/frontend.md` and `docs/api.md` if frontend-facing contract examples are added.
- Risk: Medium
- Completion evidence: Added `/admin/tournaments/[tournamentId]` route, admin server actions, documented admin API client functions, admin operation UI for sync visibility, stage/status/source/search filters, create-match, kickoff correction, final-result, and rescore workflows, plus frontend API/types updates. Fixed Reviewer findings so mutation `403` switches to a no-controls access-denied state and missing route tournaments render `NoTournamentsState` before detail calls. Existing-match team reassignment remains out of scope because no documented backend endpoint exists. Focused admin tests passed; full frontend tests passed with 34 tests; frontend lint, typecheck, and production build passed. Independent Reviewer re-review decision: `APPROVED WITH COMMENTS`, with a non-blocking note that some route/access-denied tests remain source-text assertions matching current repo style.

### UX-002: Admin Data Correction and Sync Visibility Flow

- Owner: Product Designer
- Supporting agents: Frontend, Backend
- Status: COMPLETED
- Dependencies: ARCH-003 internal data/status model; BE-005 admin API shape; DEVOPS-002 sync schedule and operational visibility.
- Objective: Specify the minimal admin experience for viewing sync status and correcting teams, kickoff times, match status, and final results.
- Context: The fallback UI is operationally critical during the tournament. It should be fast, clear, accessible, and hard to misuse.
- Relevant files: `docs/frontend.md`, `docs/backlog.md`, `docs/project-status.md`.
- Expected deliverables: Admin user flow; screen/content specification; correction forms; sync visibility; confirmation/error states; accessibility requirements; API data needs for FE-006.
- Acceptance criteria: Admins can identify stale/failed syncs, manually correct a match, confirm result changes, understand whether scoring was recalculated, and recover from provider failure without frontend business-rule duplication.
- Required tests: None for design-only work. FE-006 must add component, route, and API-client tests for the admin UI.
- Documentation updates: Added the UX-002 specification to `docs/frontend.md`; updated backlog and project status.
- Risk: Medium
- Completion evidence: Defined the `/admin/tournaments/[tournamentId]` operator flow, sync freshness/error visibility, match list content, create/kickoff/result/rescore forms, confirmation copy, loading/empty/error/recovery states, accessibility requirements, responsive behavior, and FE-006 API data needs. Documented frontend boundaries: no scoring/progression logic, no invented endpoints, stale sync inferred from match audit fields, manual sync failure from sync response errors, and existing-match team reassignment treated as an API dependency because no such endpoint is documented in `docs/api.md`.

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
- Completion evidence: Added scheduled-sync operations documentation,
  provider/sync environment variables in `.env.example` and Docker Compose, and
  the optional local `fixture-sync` Compose profile service for manual local
  sync runs. The original Render cron blueprint service from this task was
  later removed by DEVOPS-005 so the current default blueprint matches the
  free-plan path. Documented local run instructions, production runbook,
  logging/error expectations, retry guidance, manual fallback, rollback/pause
  steps, and MVP observability through scheduler logs plus match audit fields.
  Follow-up review findings were fixed by making the CLI `all` mode commit once
  only after all sync phases succeed and roll back on phase errors. Validation
  passed: YAML parse for `render.yaml` and `docker-compose.yml`; `docker compose
  --env-file .env.example --profile tools config` rendered successfully;
  `tests/config` passed; backend/script matrix passed with 53 tests;
  independent Reviewer gate found no blocking issues for BE-005/DEVOPS-002.

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
- Next executable sequence: blocked by `DEPLOY-001` external production
  deployment prerequisites.
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
