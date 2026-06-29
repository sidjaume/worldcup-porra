# ADR ARCH-003: Knockout Data Source and Result Contract

- Status: Accepted
- Date: 2026-06-29
- Owner: Architect
- Related backlog: `DATA-EPIC-001`, `BE-005`, `DEVOPS-002`, `UX-002`, `FE-006`

## Context

The MVP supports only the FIFA World Cup 2026 knockout phase and must remain
simple to operate for private pools of roughly 10-100 users. Tournament data
operations still need a documented production approach for initial bracket
creation, team assignment, kickoff changes, match status updates, result
updates, and operational recovery when automation fails.

The current planning already points toward a hybrid strategy:

- official/manual fixture seed
- approved provider for operational updates
- admin fallback
- no scraping as the primary dependency

There is also an unresolved wording gap for knockout scoring semantics. The
current backend requires a completed knockout match to have a winner and rejects
tied completed scores. Product documentation has not yet stated whether pool
scoring should use regulation time, extra-time score, or a final score that
excludes penalties.

This ADR resolves both questions so DATA-EPIC-001 can move into executable
implementation work.

## Decision

Adopt a hybrid knockout data-operations model:

1. Seed the tournament bracket from an official or manually curated source
   controlled by the project team.
2. Use one approved provider integration behind a backend-owned adapter
   boundary for operational updates.
3. Keep admin tooling as a first-class fallback for creating, correcting, or
   overriding teams, kickoff times, statuses, winners, and scores.
4. Do not use scraping as an in-app primary production dependency.

Adopt the following knockout result semantics for scoring:

1. Predictions are scored against the match score at the end of play, meaning
   after regular time or extra time.
2. Penalty shoot-out goals are excluded from exact-score and team-goal
   comparison.
3. If a match is decided on penalties after a tied score at the end of play,
   the internal result must store both the tied score and the advancing
   `winner_team_id`.
4. "Correct winner" points are awarded from the advancing team.
5. "Exact score" and single-team-goal bonuses are awarded from the tied
   end-of-play score, not from the penalty tally.

Example:

- Prediction: Spain 1-1 Portugal, Spain advances
- Actual match: 1-1 after extra time, Portugal advances on penalties
- Outcome: exact-score bonus yes, correct-winner bonus no

This means the canonical match-result contract must allow a completed knockout
match to have tied goals together with an explicit winner.

## Rationale

### Why hybrid data sourcing

- Manual or official seeding keeps the initial bracket under project control and
  avoids blocking MVP progress on provider onboarding.
- A provider-assisted flow reduces tournament-day manual work for kickoff
  changes, participant resolution, and results.
- An admin fallback is operationally necessary because private-pool software
  cannot rely on one external source being always correct and always available.
- Avoiding scraping as a primary dependency lowers legal, stability, and
  maintenance risk.

### Why end-of-play scoring semantics

- It matches how football supporters usually interpret knockout scorelines:
  penalties determine who advances, but not the match score itself.
- It avoids synthetic decisive scores for penalty shoot-out matches.
- It preserves the configured scoring system without forcing penalty prediction
  features into the MVP.
- It keeps `winner_team_id` as a separate business field instead of trying to
  infer advancement from goals alone.

## Provider Boundaries

The approved provider is an operational update source, not the owner of the
domain model.

The provider integration may update:

- external reference IDs
- home and away teams
- scheduled kickoff times
- match status
- end-of-play goals
- winner/advancing team
- provider last-updated metadata

The provider integration must not:

- decide scoring rules
- calculate rankings
- bypass authorization
- bypass audit logging
- mutate data outside backend application services

Preferred initial MVP candidate: `rezarahiminia/worldcup2026`
([GitHub](https://github.com/rezarahiminia/worldcup2026)).

Why this candidate is acceptable for MVP evaluation:

- it is published as a free open-source World Cup 2026 API
- the repository states it is licensed under ISC
- it exposes data files that can be imported under project control
- it exposes a public REST surface for matches, teams, groups, and stadiums
- it can be forked or self-hosted if the public deployment becomes unstable

Constraints on using this candidate:

- the provider candidate covers the full 104-match tournament, so our backend
  must only consume the knockout subset we support
- the hosted API must not become the only path to correctness; project-owned
  seed data and admin overrides remain mandatory
- implementation should prefer importing or self-hosting the open-source data
  path over depending blindly on third-party uptime

## Operational Model

### Seed

- Seed one canonical knockout bracket for the FIFA World Cup 2026 using an
  official or manually curated fixture source.
- Seeded records should include stable internal IDs, stage, bracket position,
  next-match linkage, and placeholder slots where teams are not yet known.

### Sync

- Run idempotent provider sync jobs to update known teams, kickoff times,
  statuses, results, and winner metadata.
- Normalize provider payloads into the internal match contract before
  persistence.
- Preserve audit metadata for last sync attempt, source, and applied changes.

### Admin fallback

- Admins must be able to correct or override any provider-managed field needed
  for tournament operations.
- Manual corrections must be visible as overrides or correction events so later
  sync runs do not silently undo them.

## Consequences

### Positive

- DATA-EPIC-001 no longer depends on choosing a named provider before design and
  implementation can begin.
- A free provider candidate now exists with an open-source codebase and data
  files, which reduces cost risk for the MVP.
- Backend and DevOps can implement toward a stable adapter boundary.
- Product wording for penalty-decided matches becomes explicit.
- Admin fallback is treated as a required operational capability.

### Negative

- The backend contract must evolve from the current "completed knockout matches
  cannot be tied" assumption.
- Provider normalization becomes slightly more complex because winner and score
  are separate concerns.
- Admin UX needs clear language so a tie plus advancing winner does not confuse
  operators.
- If the project uses the public hosted deployment directly, uptime and data
  freshness remain outside our control; self-hosting or import-first operation
  is safer.

## Rejected Alternatives

### 1. Manual-only operations

Rejected because it creates avoidable tournament-day toil and increases
operator-error risk.

### 2. Provider-only operations with no admin override

Rejected because it makes the app brittle during outages, delays, mapping
errors, or licensing changes.

### 3. Scraping as the main production source

Rejected because it adds legal, maintenance, and reliability risk that is not
appropriate for a conservative MVP.

### 4. Score against penalty shoot-out tallies

Rejected because it turns penalties into fake match goals and produces awkward
exact-score behavior.

### 5. Score only winner for penalty-decided matches

Rejected because it discards a meaningful part of the existing scoring system
and creates inconsistent behavior between regulation wins and penalty wins.

## Implementation Implications

The follow-up work should implement:

- a backend-owned provider adapter interface and normalization layer
- an adapter/import path that can read from the `worldcup2026` data model while
  filtering to the knockout subset we support
- canonical internal result semantics where completed matches may have tied
  goals plus `winner_team_id`
- updates to the current admin result workflow and validation rules, which now
  reject tied completed knockout scores
- auditability for sync attempts and manual overrides
- safe idempotent rescoring and bracket progression when provider or admin data
  changes
- admin workflows that show source-of-truth state and override state clearly

## Follow-Up Tasks

- `BE-005`: provider adapter, sync service, external mapping, audit fields, and
  normalization for tied completed scores with explicit winners
- `DEVOPS-002`: scheduling, secrets, observability, and retry/runbook guidance
- `UX-002`: operator flow for sync visibility and manual correction
- `FE-006`: admin UI for sync visibility and data correction
- `REV-003`: end-to-end review of operational readiness
