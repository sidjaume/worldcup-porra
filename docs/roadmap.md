# Development Roadmap

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

## Phase 0: Project Foundation

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

- Domain tests do not import FastAPI, SQLAlchemy, Streamlit, or external providers.

## Phase 2: Database and Repositories

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

## Phase 3: Authentication

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

- Streamlit can authenticate through backend-owned OAuth.
- Google secrets exist only in backend configuration.

## Phase 4: Pool Management

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

Deliverables:

- Match listing by tournament and stage.
- User prediction create/update endpoint.
- Prediction visibility rules.
- Streamlit prediction forms.
- Read-only state for locked/completed matches.

Tests:

- Predictions before lock succeed.
- Predictions at/after lock fail.
- Predictions for matches outside the pool tournament fail.
- Pre-lock participant predictions are hidden from other users.

Acceptance criteria:

- Users can submit and edit their predictions until match kickoff.

## Phase 6: Results, Scoring, and Rankings

Deliverables:

- Admin match result endpoint.
- Match completion workflow.
- Winner progression.
- Prediction scoring.
- Ranking endpoint.
- Streamlit ranking table.

Tests:

- Completing a match scores all relevant predictions.
- Rescoring is idempotent.
- Winner advances to configured next match slot.
- Ranking tie-breakers are deterministic.

Acceptance criteria:

- After a match result is entered, users see updated points and rankings.

## Phase 7: Streamlit MVP UX

Deliverables:

- Dashboard.
- Pool management page.
- Predictions page grouped by stage.
- Rankings page.
- Profile page.
- Reusable API client and UI components.
- User-facing error handling.

Acceptance criteria:

- A non-technical participant can log in, join a pool, submit predictions, and check rankings without backend knowledge.

## Phase 8: Deployment

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

## Phase 9: Hardening and Polish

Deliverables:

- Rate limits for auth and invite-code endpoints.
- Admin tooling for bracket corrections.
- Better audit trail for match result changes.
- More complete observability.
- Backup/restore runbook.
- Accessibility and mobile checks for Streamlit screens.

Acceptance criteria:

- Common abuse cases are handled.
- Operational recovery steps are documented.

## Suggested MVP Milestones

### Milestone 1: Testable Core

Includes phases 0-1.

Outcome: The core prediction, scoring, and bracket rules are implemented and tested independently.

### Milestone 2: Persistent Backend

Includes phases 2-4.

Outcome: Authenticated users can create and join pools backed by PostgreSQL.

### Milestone 3: Playable Pool

Includes phases 5-6.

Outcome: Users can submit predictions, admins can enter results, and rankings update.

### Milestone 4: Deployed MVP

Includes phases 7-8.

Outcome: The app is usable by a private group on Render + Neon.

### Milestone 5: Production Readiness

Includes phase 9.

Outcome: The MVP is safer to operate during the tournament.

## Early Technical Decisions

- Use FastAPI for the backend REST API.
- Use Streamlit for the frontend only.
- Use PostgreSQL on Neon for all persistence.
- Use Alembic for migrations.
- Use SQLAlchemy for ORM/repository implementation.
- Use backend-owned Google OAuth.
- Store predictions per pool, not globally per user and match.
- Store scores separately from predictions to support rescoring and scoring-version history.
- Derive rankings from prediction scores for the MVP.

## Open Questions

- Should knockout predictions allow draws after regulation time, or should users predict the final official score after extra time/penalties? The MVP should define this before implementation because it affects winner calculation.
- Who can administer tournament matches in the first release: an environment-configured admin list, pool owners, or a global admin role?
- Should invite codes be human-friendly short codes or longer URL-safe tokens? Human-friendly is easier for private groups; longer tokens reduce guessing risk.
- Should predictions become visible at kickoff or only after the match is completed?

## Possible Post-MVP Improvements

- Email notifications or reminders before match locks.
- Pool-specific scoring configurations.
- Public share links for standings.
- Admin import from external fixture/result providers.
- Materialized ranking cache for larger usage.
- Multi-language frontend.
- Audit log screen for pool owners.

