# Backlog

Last updated: 2026-06-29

## IN_PROGRESS

### ORCH-001: Architecture and Contract Reconciliation

- Owner: Architect
- Supporting agents: None for first pass
- Status: PENDING_REVIEW
- Dependencies: Current repository status inspection
- Acceptance criteria: `docs/architecture.md`, `docs/api.md`, `docs/database.md`, and `docs/roadmap.md` accurately reflect the current implementation status; unresolved contract gaps are documented as follow-up tasks; no specialist implementation is bundled into the reconciliation.
- Risk: Medium

## READY

### REV-001: Independent Production-Readiness Review

- Owner: Reviewer
- Supporting agents: Architect
- Dependencies: ORCH-001 preferred first, but review can begin from current diffs
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES REQUESTED`; findings are classified by severity with file references and required follow-up owners.
- Risk: Medium

## PLANNED

### DEVOPS-001: Environment and OAuth Configuration Audit

- Owner: DevOps
- Supporting agents: Backend
- Dependencies: Architect confirmation of backend-owned OAuth callback contract
- Acceptance criteria: `.env.example`, docs, `docker-compose.yml`, Render variables, and settings defaults agree on backend/frontend callback URLs and frontend origins; no secrets are exposed; local and production setup instructions are consistent.
- Risk: Medium

### BE-002: API Contract Alignment for Pool and Admin Endpoints

- Owner: Backend
- Supporting agents: Architect, Frontend
- Dependencies: ORCH-001 findings and API contract decision
- Acceptance criteria: `PATCH /api/v1/pools/{pool_id}` response shape, admin match completion/update semantics, and admin rescore response are either implemented to match `docs/api.md` or `docs/api.md` is intentionally narrowed with frontend types updated; affected tests are added or updated.
- Status: PLANNED
- Risk: Medium

### BE-003: Ranking Tie-Breaker Contract Alignment

- Owner: Backend
- Supporting agents: Architect
- Dependencies: Architect decision on final deterministic tie-breaker
- Acceptance criteria: Ranking implementation, `docs/api.md`, `docs/database.md`, and tests agree on tie-breakers after total points, exact scores, and correct winners.
- Status: PLANNED
- Risk: Low

### BE-004: API Error Format Standardization Review

- Owner: Backend
- Supporting agents: Reviewer
- Dependencies: REV-001 findings
- Acceptance criteria: Expected service/domain/auth errors and request validation errors either all use the standard `{ "error": { "code", "message", "details" } }` body, or accepted exceptions are documented in `docs/api.md`.
- Status: PLANNED
- Risk: Low

### BE-001: Repository and Migration Integration Coverage

- Owner: Backend
- Supporting agents: DevOps
- Dependencies: Local PostgreSQL or CI service database availability
- Acceptance criteria: Migration smoke test and repository integration tests cover schema recreation, key constraints, pool membership, prediction upsert, and ranking query behavior.
- Risk: Medium

### UX-001: Product Designer Usability and Accessibility Pass

- Owner: Product Designer
- Supporting agents: Frontend, Reviewer
- Dependencies: Current Next.js screens
- Acceptance criteria: Critical user flows are reviewed for mobile layout, focus states, labels, contrast, loading, empty, and error states; findings are converted into frontend tasks.
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
