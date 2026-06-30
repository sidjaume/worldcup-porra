# ADR ARCH-004: Knockout Operations Remediation Contract

- Status: Accepted
- Date: 2026-06-29
- Owner: Architect
- Related backlog: `ARCH-004`, `BE-007`, `BE-008`, `BE-009`, `BE-010`, `DEVOPS-004`, `FE-008`, `REV-003`
- Supersedes: none
- Extends: [ARCH-003](./arch-003-knockout-data-source-and-result-contract.md)

## Context

REV-003 returned `CHANGES_REQUESTED` for the knockout operations slice. The
findings are contract-level, not only implementation bugs:

- Predictions can store tied goals, but cannot say which tied team advances.
- Admin fallback can complete results and correct kickoff, but cannot correct
  existing-match teams or operational statuses.
- Provider sync can indirectly overwrite downstream bracket slots after manual
  corrections.
- Provider normalization must fail closed for unknown statuses and preserve
  legitimate zero scores.
- Operations documentation assumes Render cron even though the current
  no-paid-plan path requires local scheduled sync against Neon.

ARCH-003 remains the source of truth for the hybrid seed/provider/admin model
and end-of-play scoring semantics. This ADR narrows the additional MVP contract
needed to satisfy REV-003 without adding group-stage management, arbitrary
bracket editing, or a full operations console.

## Decision

### 1. Tied Prediction Advancing Winner

Add `predicted_winner_team_id` to predictions.

Rules:

- `predicted_winner_team_id` is required only when
  `predicted_home_goals == predicted_away_goals`.
- For tied predictions, the value must be either the match `home_team_id` or
  `away_team_id`.
- For non-tied predictions, the predicted winner is derived from the predicted
  goals and `predicted_winner_team_id` must be omitted or `null`.
- A tied prediction is valid only when both match teams are known.
- Correct-winner scoring uses `predicted_winner_team_id` for tied predictions
  and the goal-implied side for non-tied predictions.
- Exact-score and single-team-goal bonuses continue to use only end-of-play
  goals.

API impact:

- `PUT /api/v1/pools/{pool_id}/matches/{match_id}/prediction` accepts and
  returns `predicted_winner_team_id`.
- Prediction list and match-prediction visibility responses include
  `predicted_winner_team_id`.

Database impact:

- Add nullable `predictions.predicted_winner_team_id` referencing `teams.id`.
- Service/domain validation enforces the conditional requirement and same-match
  team membership.

Frontend impact:

- Prediction forms must show an advancing-winner control only when the entered
  score is tied.
- The frontend may validate required selection for fast feedback, but the
  backend remains authoritative.

### 2. Existing-Match Admin Corrections

Keep admin fallback small and explicit. Add two endpoints for existing matches:

```text
PATCH /api/v1/admin/matches/{match_id}/teams
PATCH /api/v1/admin/matches/{match_id}/status
```

`PATCH /teams` updates `home_team_id` and/or `away_team_id`.

Rules:

- Admin-only.
- Allowed only before match completion.
- Either team may be `null` for an unresolved slot.
- If both teams are present, they must belong to the match tournament and be
  distinct.
- The endpoint sets `sync_source="admin"` and `admin_override=true`.
- It does not score predictions, complete the match, or edit bracket linkage.

`PATCH /status` updates operational status.

Rules:

- Admin-only.
- Accepts `scheduled`, `locked`, `in_progress`, and `cancelled`.
- Does not accept `completed`; completion must continue through
  `PATCH /api/v1/admin/matches/{match_id}` with result fields.
- Does not reopen completed matches in the MVP.
- Sets `sync_source="admin"` and `admin_override=true`.
- Does not change scores, teams, kickoff time, or bracket linkage.

This intentionally avoids a generic match patch endpoint. Completion, kickoff,
team correction, status correction, sync, and rescore remain separate commands.

### 3. Provider And Manual Override Boundaries

Manual corrections take precedence over provider data.

Provider sync must not mutate provider-managed fields on a match where
`admin_override=true`. For MVP this protection is match-level, not field-level.
The sync may report the skipped row as a conflict or warning, but must not
silently overwrite the manual value.

Bracket progression rules:

- Admin result completion/correction may write the winner into the configured
  downstream match slot and must mark the downstream match
  `admin_override=true` when it changes that slot.
- Provider progression may fill a downstream slot only when the downstream
  match is not manually overridden and the target slot is empty or already
  contains the same team.
- If provider progression wants to replace a populated downstream slot with a
  different team, it must fail closed for that slot and report a sync error or
  conflict.
- Provider sync must never clear `admin_override`.

The MVP does not add a "clear override" workflow. If that becomes necessary,
it should be a separate Architect-reviewed admin contract.

### 4. Provider Normalization Fail-Closed Behavior

Provider normalization must be explicit.

Rules:

- Unknown provider statuses are errors. They must not default to `scheduled`.
- A provider row with an unknown status must not mutate match state.
- Numeric zero is a valid score value and must not be treated as missing.
- `null` or absent score fields mean unknown score, not zero.
- A completed provider result must include valid end-of-play scores and an
  advancing winner. Missing winner or missing score data for a completed match
  is a sync error.
- The sync response should include errors for failed rows while preserving
  already-valid existing data.

### 5. Free-Plan Sync Operations

Render cron remains an optional production convenience, not an MVP assumption.

The current no-paid-plan operational path is:

1. Backend and frontend run on Render services.
2. PostgreSQL runs on Neon.
3. Scheduled fixture sync can run from a trusted local or operator-controlled
   machine against Neon using the documented sync script and environment
   variables.
4. Admin-triggered sync and manual corrections remain available from the app as
   fallback.

Render cron can be enabled later when the chosen Render plan supports it and
the tournament UUID/provider variables are configured. Until then, docs must not
state that production sync depends on an enabled Render cron service.

## Options Considered

### Option A: Add only `predicted_winner_team_id` for tied predictions

Accepted. It is the smallest contract that satisfies ARCH-003 penalty-decided
semantics without adding penalty shoot-out prediction features.

### Option B: Require predicted winner for every prediction

Rejected for MVP. It duplicates information for non-tied predictions and adds
avoidable UI friction.

### Option C: Add a generic admin match patch endpoint

Rejected. A broad endpoint would blur command boundaries and increase the risk
of accidental scoring, status, or bracket side effects.

### Option D: Field-level manual override tracking

Deferred. It is more precise, but requires more schema and UI complexity. A
match-level `admin_override` is safer and sufficient for the private-pool MVP.

### Option E: Provider sync defaults unknown statuses to `scheduled`

Rejected. Failing open hides upstream changes and can corrupt operational state.

### Option F: Render cron as required production architecture

Rejected for the current free-plan path. It can remain documented as optional,
but local scheduled sync against Neon is the production-safe no-paid fallback.

## Consequences

### Positive

- Backend and frontend can implement tied-score predictions without inventing a
  scoring contract.
- Admin fallback covers the minimum operational corrections needed during the
  knockout phase.
- Manual corrections cannot be silently undone by later provider runs.
- Provider adapter failures become visible and recoverable.
- Deployment docs match the current cost constraints.

### Negative

- A migration is required for `predictions.predicted_winner_team_id`.
- Match-level override protection can skip more provider updates than strictly
  necessary.
- Local scheduled sync depends on an operator-controlled machine being online
  unless Render cron or another scheduler is enabled later.

## Follow-Up Task Sequencing

1. `BE-008`: add prediction advancing-winner API, domain, persistence, scoring,
   and tests.
2. `BE-009`: add existing-match team and status correction endpoints with
   override/audit behavior.
3. `BE-007`: harden provider/manual override protection for downstream slots.
4. `BE-010`: harden provider normalization for unknown statuses and zero scores.
5. `DEVOPS-004`: update the free-plan sync runbook and environment guidance.
6. `FE-008`: align frontend status typing.
7. Frontend follow-up for tied prediction and admin correction UI should be
   scheduled after BE-008 and BE-009 expose the documented API contract.
8. `REV-003`: rerun focused review after remediation tasks pass their checks.

## Acceptance Criteria Refinements

- Backend implementation must include domain/service tests for tied predictions,
  provider overwrite conflicts, unknown statuses, and zero scores.
- API contract tests must prove request/response shapes include
  `predicted_winner_team_id` where documented.
- Migration tests must cover the new prediction column.
- Frontend tests must cover tied-score winner selection and status display once
  the UI changes are implemented.
- DevOps documentation review must confirm Render cron is optional and local
  scheduled sync against Neon is documented without committing secrets.
