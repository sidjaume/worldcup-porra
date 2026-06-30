# Backlog

Last updated: 2026-06-30

## IN_PROGRESS

None.

## PENDING_REVIEW

None.

## PLANNED

### BE-013: Provider Result Sync Progression Conflict Resolution

- Owner: Backend
- Supporting agents: Architect, DevOps, Reviewer
- Status: PLANNED
- Dependencies: ARCH-003 result semantics, BE-005 provider sync, BE-007 manual override protection, production provider fixture evidence.
- Current decision: The product target is fully automatic tournament operations. Production may stay temporarily on `TOURNAMENT_SYNC_MODE=matches` only until provider result sync is made safe.
- Objective: Resolve the current provider completed-result progression conflicts so automated `TOURNAMENT_SYNC_MODE=all` or `results` can be enabled without overwriting seeded/manual bracket links or corrupting scoring/rankings.
- Acceptance criteria: Provider completed-result sync processes real completed knockout matches safely in a controlled environment; conflict handling is covered by tests; scheduler guidance states the exact conditions for enabling `all`/`results`; completed results do not require routine manual admin entry once this task is done.
- Risk: High

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
- Next executable sequence: resolve BE-013, then switch scheduled production sync from `matches` to the approved automatic result-sync mode.
- Acceptance criteria: The app can initialize knockout fixtures, sync teams/times/results from an approved source, audit changes, handle provider failure through admin fallback, and recalculate scoring idempotently after finished matches.
- Risk: High

## BLOCKED

None.

## DEFERRED

### HARDEN-001: Rate Limiting and Abuse Protection

- Owner: Backend
- Supporting agents: Architect, DevOps, Reviewer
- Dependencies: MVP flow stabilization
- Acceptance criteria: Auth and invite-code endpoints have appropriate rate limiting or abuse mitigation.
- Risk: Medium
