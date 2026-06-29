# Development Roadmap

Status: MVP implementation slices exist; REV-002 follow-up work is approved and archived; production configuration remains blocked on external accounts and secrets.
Last reconciled: 2026-06-29.

Implementation has already begun. This roadmap now describes the intended
delivery phases, their current status, and the gates still required before the
work can be treated as merge-ready or production-ready.

## Guiding Strategy

Build the MVP as a modular monolith with strong domain boundaries before adding operational complexity. The first production-ready release should support a small private group end to end:

- Google login
- Pool creation and joining
- Knockout match browsing
- Prediction submission before lock time
- Match result entry by an admin
- Scoring
- Rankings
- Render + Neon deployment

## Review Gates

Architecture reconciliation and Reviewer approval are required before the
current implementation is treated as merge-ready.

Review checklist:

- Architecture follows `AGENTS.md` and `.agents/architect.md`.
- Backend owns business rules and persistence.
- Frontend/backend contract is documented.
- PostgreSQL schema supports the MVP without group-stage concepts.
- API endpoints are RESTful and predictable.
- Deployment target is Render + Neon.
- No secrets are stored in the repository.

Each phase should finish with:

- Tests appropriate to risk.
- Updated documentation when contracts change.
- Reviewer approval before moving to the next phase.

Current gate status:

- Architecture/API/database/roadmap reconciliation: approved with comments under ORCH-001.
- Focused production-readiness review: REV-002 completed with changes requested; split follow-ups are approved and archived.
- Historical follow-up: FE-007 is approved with comments, ORCH-001 is approved with comments, BE-006/DEVOPS-003 are approved, and ARCH-003 is accepted. DATA-EPIC-001 is ready for implementation sequencing starting with BE-005.
- Production deployment: blocked until Render, Neon, Google OAuth, and secrets are configured outside the repository.
- OAuth/environment alignment: completed under DEVOPS-001.

## Phase 0: Project Foundation

Status: Implemented, pending Reviewer validation.

Deliverables:

- Python project structure under `app/` and `frontend/`.
- Dependency management with pinned production dependencies.
- Formatter, linter, and test runner.
- Environment settings module.
- Dockerfiles for backend and frontend.
- Local development setup with `.env.example`.
- CI check for formatting, linting, and tests.

Acceptance criteria:

- Backend test command runs successfully.
- Frontend starts locally.
- Backend exposes `/health`.
- No secrets are committed.

## Phase 1: Domain Layer

Status: Implemented, pending Reviewer validation.

Deliverables:

- Domain enums for stages, match status, prediction status, and slots.
- Pure scoring engine with configurable rules.
- Prediction lock policy.
- Knockout progression service.
- Domain exceptions.

Tests:

- Correct winner scoring.
- Exact score scoring.
- Partial score scoring.
- Draw/tie handling policy for knockout predictions.
- Prediction lock before and after scheduled time.
- Winner advancement into next match home/away slot.

Acceptance criteria:

- Domain tests do not import FastAPI, SQLAlchemy, frontend framework code, or external providers.

## Phase 2: Database and Repositories

Status: Implemented initial slice, pending Backend/Reviewer validation.

Deliverables:

- SQLAlchemy models.
- Alembic migrations.
- Repository classes.
- Initial seed script for tournament, teams, and bracket structure.
- Ranking query or view.

Tests:

- Repository integration tests against PostgreSQL.
- Migration smoke test.
- Unique constraints and prediction upsert behavior.

Acceptance criteria:

- Schema can be recreated from migrations.
- No application feature depends on local files for persistence.

Known follow-up: repository integration tests and migration smoke tests are
tracked as `BE-001` in `docs/backlog.md`.

## Phase 3: Authentication

Status: Implemented initial slice; OAuth configuration audit completed; REV-002 follow-up work is approved and archived.

Deliverables:

- Google OAuth start and callback endpoints.
- User provisioning.
- Application access and refresh tokens.
- Refresh-token rotation and logout.
- Auth middleware/dependencies.
- Current-user profile endpoint.

Tests:

- OAuth callback service with mocked Google identity.
- Token validation and expiry.
- Refresh-token rotation.
- Unauthorized and forbidden API cases.

Acceptance criteria:

- The frontend can authenticate through backend-owned OAuth.
- Google secrets exist only in backend configuration.

Known follow-up: real OAuth credentials and deployed callback/origin values must
be configured outside the repository before production deployment.

## Phase 4: Pool Management

Status: Implemented initial slice, pending API contract review and Reviewer validation.

Deliverables:

- Create pool.
- Join pool by invite code.
- Rotate invite code.
- List current user's pools.
- List and remove participants.
- Pool membership authorization checks.

Tests:

- Owner is added as participant.
- Duplicate joins are rejected or idempotently handled.
- Non-members cannot access pool resources.
- Removed participants cannot submit predictions.

Acceptance criteria:

- A logged-in user can create a private pool and another logged-in user can join it.

## Phase 5: Tournament and Predictions

Status: Implemented initial slice, pending Reviewer validation.

Deliverables:

- Match listing by tournament and stage.
- User prediction create/update endpoint.
- Prediction visibility rules.
- Frontend prediction forms.
- Read-only state for locked/completed matches.

Tests:

- Predictions before lock succeed.
- Predictions at/after lock fail.
- Predictions for matches outside the pool tournament fail.
- Pre-lock participant predictions are hidden from other users.

Acceptance criteria:

- Users can submit and edit their predictions until match kickoff.

## Phase 6: Results, Scoring, and Rankings

Status: Implemented initial slice, pending Reviewer validation.

Deliverables:

- Admin match result endpoint.
- Match completion workflow.
- Winner progression.
- Prediction scoring.
- Ranking endpoint.
- Frontend ranking table.

Tests:

- Completing a match scores all relevant predictions.
- Rescoring is idempotent.
- Winner advances to configured next match slot.
- Ranking tie-breakers are deterministic.
- Penalty-decided matches preserve the tied end-of-play score while still
  recording the advancing winner.

Acceptance criteria:

- After a match result is entered, users see updated points and rankings.

## Phase 7: Frontend MVP UX

Status: Implemented initial slice, pending Product Designer/Reviewer validation.

Deliverables:

- Next.js app structure with React, TypeScript, and Tailwind CSS.
- Dashboard.
- Pool management page.
- Predictions page grouped by stage.
- Rankings page.
- Profile page.
- Reusable typed API client and UI components.
- User-facing error handling.
- Responsive mobile-first layouts.

Acceptance criteria:

- A non-technical participant can log in, join a pool, submit predictions, and check rankings without backend knowledge.
- Frontend does not duplicate backend scoring, locking, ranking, membership, or bracket progression logic.

## Phase 8: Deployment

Status: Local Docker/Render blueprint implemented; production deployment blocked.

Deliverables:

- Backend Render web service.
- Frontend Render web service.
- Neon production database.
- Production environment variables.
- Alembic migration runbook.
- Health checks.
- Basic structured logs.

Acceptance criteria:

- Backend binds to Render `$PORT`.
- Frontend binds to Render `$PORT`.
- Backend health check passes.
- Production database uses Neon connection string with SSL.
- Production deploy can be repeated from a clean environment.

Known follow-up: production Render + Neon deployment remains blocked until real
external accounts, OAuth client configuration, and production secrets exist.

## Phase 9: Hardening and Polish

Status: Planned/deferred. World Cup knockout data operations are tracked as
`DATA-EPIC-001` in `docs/backlog.md`; `ARCH-003` now defines the target
contract and implementation order.

Deliverables:

- Rate limits for auth and invite-code endpoints.
- Admin tooling for bracket corrections.
- Official/manual bracket seed plus one approved provider adapter for
  operational updates.
- Preferred initial free candidate: `rezarahiminia/worldcup2026`, consumed
  through project-controlled import or self-hosted adapter flow.
- Scheduled synchronization for kickoff times, teams, match status, and results.
- Manual fallback workflow for correcting match data and triggering rescoring.
- Better audit trail for match result changes.
- More complete observability.
- Backup/restore runbook.
- Accessibility and mobile checks for frontend screens.

Acceptance criteria:

- Common abuse cases are handled.
- Operational recovery steps are documented.
- Tournament data sync is idempotent, observable, and recoverable during match days.

Operational contract from ARCH-003:

- Seed the bracket from an official or manually curated source under project
  control.
- Use provider updates for operational freshness, not as the only path to
  correctness.
- Allow admin overrides with auditability.
- Score penalty-decided matches from end-of-play goals while using
  `winner_team_id` for advancement and correct-winner points.

## Suggested MVP Milestones

### Milestone 1: Testable Core

Includes phases 0-1.

Outcome: The core prediction, scoring, and bracket rules are implemented and tested independently.

Status: Implemented, pending review.

### Milestone 2: Persistent Backend

Includes phases 2-4.

Outcome: Authenticated users can create and join pools backed by PostgreSQL.

Status: Implemented initial slice, pending review and OAuth config audit.

### Milestone 3: Playable Pool

Includes phases 5-6.

Outcome: Users can submit predictions, admins can enter results, and rankings update.

Status: Implemented initial slice, pending review.

### Milestone 4: Deployed MVP

Includes phases 7-8.

Outcome: The app is usable by a private group on Render + Neon.

Status: In progress. Local Docker stack is documented as healthy in
`docs/project-status.md`; production deployment is not complete.

### Milestone 5: Production Readiness

Includes phase 9.

Outcome: The MVP is safer to operate during the tournament.

Status: Planned/deferred.

## Early Technical Decisions

- Use FastAPI for the backend REST API.
- Use Next.js, React, TypeScript, and Tailwind CSS for the production frontend.
- Use the Next.js frontend as the product-facing UI.
- Use PostgreSQL on Neon for all persistence.
- Use Alembic for migrations.
- Use SQLAlchemy for ORM/repository implementation.
- Use backend-owned Google OAuth.
- Store predictions per pool, not globally per user and match.
- Store scores separately from predictions to support rescoring and scoring-version history.
- Derive rankings from prediction scores for the MVP.

## Open Questions

- Who can administer tournament matches in the first release: an environment-configured admin list, pool owners, or a global admin role? Current implementation uses `ADMIN_EMAILS`.
- Should invite codes be human-friendly short codes or longer URL-safe tokens? Human-friendly is easier for private groups; longer tokens reduce guessing risk.
- Should predictions become visible at kickoff or only after the match is completed? Current implementation reveals all match predictions after the match locks, not only after completion.

## Possible Post-MVP Improvements

- Email notifications or reminders before match locks.
- Pool-specific scoring configurations.
- Public share links for standings.
- Additional provider integrations beyond the approved MVP tournament data source.
- Materialized ranking cache for larger usage.
- Multi-language frontend.
- Audit log screen for pool owners.
