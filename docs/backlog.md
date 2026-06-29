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

## CHANGES_REQUESTED

### UX-001: Product Designer Usability and Accessibility Pass

- Owner: Product Designer
- Supporting agents: Frontend, Reviewer
- Dependencies: Current Next.js screens
- Acceptance criteria: Critical user flows are reviewed for mobile layout, focus states, labels, contrast, loading, empty, and error states; findings are converted into frontend tasks.
- Status: CHANGES_REQUESTED
- Risk: Medium
- Findings: Mobile navigation/current-page context, mobile rankings/participants, focus-visible states, prediction input labeling/status handling, route-level loading/error states, announced form feedback, color contrast, invite-code rotation safety, and rankings label clarity need frontend follow-up.

## READY

### REV-002: Focused Production-Readiness Re-review

- Owner: Reviewer
- Supporting agents: Architect
- Dependencies: DONE technical fixes and UX findings converted into frontend tasks
- Acceptance criteria: Review decision is recorded as `APPROVED`, `APPROVED WITH COMMENTS`, or `CHANGES_REQUESTED`; findings are classified by severity with file references and required follow-up owners.
- Risk: Medium

## COMPLETED_REVIEW

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
