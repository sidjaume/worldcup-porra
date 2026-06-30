# Frontend Design

## Direction

The production frontend target is a responsive Next.js application built with:

- React
- TypeScript
- Tailwind CSS
- REST API calls to the FastAPI backend

The product-facing frontend is a Next.js application. The earlier Streamlit
prototype has been removed from the frontend tree.

## Goals

- Let users sign in with Google.
- Let users create, select, and join private pools.
- Let users submit and edit match predictions before backend lock time.
- Let users view rankings and their profile.
- Keep all business rules in the backend.
- Keep the frontend mobile-first and usable on desktop.

## Non-Goals

- No scoring logic in React components.
- No prediction-lock calculations in the frontend.
- No database access from the frontend.
- No Google client secret in frontend code.
- No group-stage UI.

## Proposed Structure

```text
frontend/
  app/
    layout.tsx
    page.tsx
    auth/
      callback/
        page.tsx
    pools/
      page.tsx
      [poolId]/
        page.tsx
        predictions/
          page.tsx
        rankings/
          page.tsx
    profile/
      page.tsx
  components/
    auth/
    layout/
    pools/
    predictions/
    rankings/
  lib/
    api/
    auth/
    config.ts
  types/
    api.ts
  styles/
    globals.css
```

## API Integration

The frontend should call only documented backend endpoints under `/api/v1`.

Required client modules:

- `lib/api/auth.ts`
- `lib/api/pools.ts`
- `lib/api/tournaments.ts`
- `lib/api/predictions.ts`
- `lib/api/rankings.ts`
- `lib/api/users.ts`

All API errors should be normalized into user-facing messages using the backend error shape:

```json
{
  "error": {
    "code": "prediction_locked",
    "message": "Predictions are closed for this match.",
    "details": {}
  }
}
```

## Authentication

The backend remains the OAuth owner.

Expected flow:

1. User clicks login.
2. Frontend redirects to `/api/v1/auth/google/start?redirect_uri=<frontend_callback>`.
3. Backend redirects to Google.
4. Backend handles Google callback and redirects to frontend callback with one-time code.
5. Frontend exchanges the code through `/api/v1/auth/exchange`.
6. Frontend stores auth state and uses bearer access tokens for API calls.
7. Frontend refreshes tokens through `/api/v1/auth/refresh`.
8. Logout calls `/api/v1/auth/logout`.

Preferred production token handling:

- Store refresh token in an HTTP-only cookie managed by a Next.js server route.
- Keep access token short-lived.
- Avoid localStorage for refresh tokens.

## UX Requirements

- Mobile-first layout.
- Clear selected pool context.
- Prediction forms must show read-only states for locked/completed matches.
- Tied-score prediction forms must require an advancing-winner selection from
  the two match teams and send `predicted_winner_team_id`.
- Backend validation errors must be visible near the relevant action.
- Rankings must be easy to scan on mobile and desktop.
- Profile edits should be minimal and focused.

## ARCH-004 Frontend Contract Notes

Prediction UI:

- `predicted_winner_team_id` is required only when the entered prediction score
  is tied.
- For non-tied predictions, omit `predicted_winner_team_id` or send `null`.
- The advancing-winner control must offer only the match home and away teams.
- Do not offer tied-score prediction submission while either team is `TBD`.
- The backend remains authoritative for validation and scoring.

Admin operations UI:

- Existing-match team correction must use
  `PATCH /api/v1/admin/matches/{match_id}/teams`.
- Existing-match status correction must use
  `PATCH /api/v1/admin/matches/{match_id}/status`.
- Status displays and filters must handle `scheduled`, `locked`,
  `in_progress`, `completed`, and `cancelled`.
- The frontend must not clear manual overrides or simulate provider overwrite
  decisions. It should surface backend success/errors from sync and correction
  endpoints.

Operations assumption:

- Render cron is optional. Operator-facing copy should not imply that scheduled
  sync is always running; show freshness from the API fields that are actually
  present.

## UX-002: Admin Data Correction and Sync Visibility Flow

Status: Completed product/UX specification for FE-006.

### Objective

Give tournament admins a compact operational screen for the knockout bracket so
they can see whether provider sync data is fresh, recover from provider
failure, and manually correct the minimum data that affects predictions,
locking, scoring, rankings, and bracket progression.

This is an operator workflow, not a marketing or analytics surface. It should
feel like the existing authenticated app: plain language, compact cards/tables,
clear form labels, visible feedback, and backend-owned business rules.

### Scope

In scope for the minimal admin experience:

- View knockout matches by stage.
- See match sync source, manual override state, and provider last-synced time.
- Run the documented provider sync for a tournament.
- Identify stale provider data from match audit fields.
- Identify a failed manual provider sync from the sync response errors.
- Create a missing match only through the documented admin match creation
  endpoint.
- Correct kickoff time for non-completed matches.
- Enter or correct final end-of-play score and advancing winner, which marks the
  match as completed through the documented completion endpoint.
- Rescore a completed match.
- Recover from provider failure by manually correcting affected matches.

Out of scope for FE-006:

- Frontend scoring logic.
- Frontend bracket-progression logic.
- Database edits or direct provider calls.
- New auth/authorization behavior.
- New backend endpoints.
- Group-stage management.
- Persistent scheduled-sync failure history beyond the data exposed by the
  current API.
- Arbitrary status transitions such as cancel, reopen, or move back to scheduled
  unless a future API contract documents them.

### Navigation

Preferred route:

- `/admin/tournaments/[tournamentId]`

Entry behavior:

- The route requires an authenticated session.
- Backend authorization remains the source of truth. If the admin endpoints
  return `403`, show an access-denied route state with no admin controls.
- Because the current user profile contract does not expose an admin role, FE-006
  should not invent role checks. A main-navigation admin link may be added only
  if the frontend can determine admin access from a documented source. Otherwise
  the operator route can be reached directly/bookmarked for MVP.

### Page Structure

The page has four compact areas, in this order on mobile:

1. Header
2. Sync visibility and action panel
3. Filters
4. Match operations list

On desktop, keep the same order but allow the sync panel and filter controls to
sit in a two-column header band. Do not introduce a landing page, hero, or
separate dashboard unless FE-006 later has a documented need.

### Header Content

Display:

- Page title: `Tournament operations`
- Tournament name and year.
- Short helper text: `Review provider sync and correct knockout match data.`
- Last visible provider sync time, derived from the latest
  `provider_last_synced_at` across loaded matches.

Do not show implementation details such as cron commands or provider payloads.

### Sync Visibility

The sync panel should summarize the operational state with text and badges:

- `Fresh`: at least one loaded match has `provider_last_synced_at` within the
  freshness window.
- `Stale`: the latest loaded `provider_last_synced_at` is older than the
  freshness window.
- `Not synced`: no loaded match has `provider_last_synced_at`.
- `Manual overrides`: count of loaded matches with `admin_override=true`.
- `Sync failed`: shown after a manual sync response includes one or more
  `errors`.

Freshness window:

- Use 30 minutes for MVP because DEVOPS-002 schedules production sync every 15
  minutes during tournament operations.
- This is a frontend display threshold only. It must not change prediction lock,
  scoring, or provider behavior.

Sync action:

- Primary action: `Run sync`.
- Confirm before running: `Provider sync can update teams, kickoff times,
  statuses, and results. Manual overrides will be preserved by the backend.`
- While pending, disable the button and show an inline loading state.
- On success with no errors, show the response counts:
  `Teams created`, `Teams updated`, `Matches created`, `Matches updated`.
- On success with errors, show an alert-style panel with the errors returned by
  the backend and a next action: `Review affected matches and correct them
  manually.`
- On network/API failure, show the normalized backend error message and keep
  existing match data visible.

Important limitation:

- The current API exposes match-level provider sync timestamps and manual sync
  errors, but not a persistent scheduled-sync run log. FE-006 can show stale data
  and the latest manual sync failure in the current page session. A persistent
  sync-failure history would require a documented backend/API addition and is
  outside UX-002.

### Filters

Provide compact controls:

- Stage tabs using the existing stage order.
- Status filter: `All`, `Scheduled`, `Locked`, `In progress`, `Completed`,
  `Cancelled`.
- Source filter: `All`, `Provider`, `Manual override`, `Not synced`.
- Search input for team name or bracket position.

Filters must be client-side for the loaded tournament data except for the
documented `stage` query on `GET /api/v1/tournaments/{tournament_id}/matches`.
Do not add new filter query parameters unless the API contract changes.

### Match Operations List

Mobile:

- Render matches as stacked cards with one match per card.
- Put the primary match identity first: stage, bracket position, teams, kickoff.
- Keep action buttons full width or two per row when space allows.

Desktop:

- A dense table or two-column card grid is acceptable.
- If using a table, preserve accessible row labels and avoid hidden actions that
  require hover.

Each match item must show:

- Stage label and bracket position.
- Home team and away team, using `TBD` when unknown.
- Kickoff time in the user's locale.
- Status.
- Score if available.
- Advancing winner if available.
- `sync_source`.
- `provider_last_synced_at` if available.
- `admin_override` badge when true.
- A stale/not-synced badge when applicable.

Actions per match:

- `Correct kickoff`: enabled only for non-completed matches.
- `Correct teams`: enabled only for non-completed matches after the documented
  team-correction endpoint is implemented.
- `Correct status`: enabled only for non-completed matches after the documented
  status-correction endpoint is implemented.
- `Enter result` or `Correct result`: enabled when both teams are known.
- `Rescore`: enabled only for completed matches.

Create action:

- Provide a `Create match` action for missing knockout fixtures only when FE-006
  implements the documented `POST /api/v1/admin/tournaments/{tournament_id}/matches`
  endpoint.
- Team and status correction for an existing match must use the documented
  ARCH-004 endpoints. The frontend must not fake these operations locally.

### Correction Forms

Use focused dialogs or inline edit panels. Dialogs must have a clear title,
initial focus, keyboard dismissal, and focus return to the triggering button.

#### Create Match

Fields:

- Stage.
- Bracket position.
- Kickoff date/time.
- Home team, optional.
- Away team, optional.

Rules:

- Team options come from `GET /api/v1/tournaments/{tournament_id}/teams`.
- Allow `TBD` by leaving a team empty when the backend accepts null team IDs.
- Prevent selecting the same team twice in the client as a convenience, but let
  the backend remain authoritative.
- Advanced bracket-link fields such as next match and next slot should stay out
  of the minimal UI unless the API contract documents them for frontend use.

Confirmation:

- Required before create.
- Copy: `Create this knockout match? Review stage, position, teams, and kickoff
  before saving.`

#### Correct Kickoff

Fields:

- New kickoff date/time.

Content:

- Show current kickoff and proposed kickoff before submission.
- Explain that the backend uses kickoff time for prediction locking.

Confirmation:

- Required when the new kickoff is earlier than the current kickoff, crosses the
  current time, or changes a match that already has submitted predictions.
- Copy: `Changing kickoff can change whether predictions are editable. Save this
  correction?`

Success state:

- `Kickoff updated. This match is now marked as a manual override.`

#### Enter Or Correct Result

Fields:

- Home goals.
- Away goals.
- Advancing winner, selected from the two match teams.

Content:

- Label goals as end-of-play goals.
- For tied scores, show helper text:
  `For penalty-decided matches, enter the tied end-of-play score and choose the
  advancing team. Do not include penalty shoot-out goals.`

Confirmation:

- Always required.
- First completion copy:
  `Save final result? The backend will advance the winner and score predictions.`
- Correction copy for an already completed match:
  `Update this final result? Rankings may change after predictions are
  rescored.`

Success state:

- `Result saved. Scoring was recalculated for this match.`

Do not display guessed point changes. The current admin endpoints return
`MatchRead`, not a scoring-delta summary.

#### Rescore

Purpose:

- Recalculate prediction scores for a completed match when the result is already
  correct but scores need to be refreshed.

Confirmation:

- Required.
- Copy: `Recalculate scores for this completed match? Rankings may change.`

Success state:

- `Scores recalculated for this match.`

### Loading, Empty, Error, And Recovery States

Route loading:

- Show the existing route loading pattern with a short message such as
  `Loading tournament operations...`.

Empty states:

- No tournaments: `No tournaments are available.`
- No matches in selected stage: `No matches are available for this stage yet.`
- No teams: `No teams are available yet. Run sync before creating matches.`

Authorization errors:

- `401`: redirect through the existing authenticated-session flow.
- `403`: show `Admin access is required.` and no controls.

Provider failure:

- Keep the current match list visible.
- Show sync errors near the sync action.
- Offer manual correction actions on the affected match list rather than a
  separate recovery workflow.

Form errors:

- Show backend validation messages near the form action and associate them with
  the relevant form using `aria-describedby`.
- Keep entered values in place after errors.

### Accessibility Requirements

- All controls must be reachable by keyboard.
- Every form input must have a visible label.
- Do not rely on badge color alone; include text such as `Stale`, `Manual
  override`, or `Sync failed`.
- Use `role="status"` for successful async updates.
- Use `role="alert"` for failed saves and sync errors.
- Disable duplicate submissions while requests are pending.
- Preserve visible `focus-visible` styling consistent with the existing UI.
- Dialogs must trap focus while open and return focus on close.
- Action labels must include the object when ambiguity is possible, for example
  `Correct kickoff for Round of 16 #3`.
- Dates should be rendered in the user's locale, but API payloads must remain
  ISO 8601 UTC.

### Responsive Behavior

- Mobile first: sync summary, filters, and match cards stack vertically.
- Stage tabs and dense filters may scroll horizontally with visible labels.
- Match actions wrap without truncating text.
- Desktop may use a table, but the mobile card layout is the source of truth for
  content priority.
- Confirmation dialogs must fit narrow screens without clipped buttons or
  hidden form fields.

### API Data Needs For FE-006

FE-006 should consume only documented `/api/v1` endpoints:

- `GET /api/v1/tournaments`
- `GET /api/v1/tournaments/{tournament_id}/teams`
- `GET /api/v1/tournaments/{tournament_id}/matches`
- `GET /api/v1/tournaments/{tournament_id}/matches?stage=<stage>`
- `POST /api/v1/admin/tournaments/{tournament_id}/sync`
- `POST /api/v1/admin/tournaments/{tournament_id}/matches`
- `PATCH /api/v1/admin/matches/{match_id}/kickoff`
- `PATCH /api/v1/admin/matches/{match_id}/teams`
- `PATCH /api/v1/admin/matches/{match_id}/status`
- `PATCH /api/v1/admin/matches/{match_id}`
- `POST /api/v1/admin/matches/{match_id}/rescore`

Frontend types for `Match` must include the documented audit fields:

- `sync_source: string | null`
- `admin_override: boolean`
- `provider_last_synced_at: string | null`

Frontend types should add admin request/response shapes for:

- `SyncTournamentRequest`
- `SyncResult`
- `CreateMatchRequest`
- `CompleteMatchRequest`
- `UpdateKickoffRequest`
- `UpdateMatchTeamsRequest`
- `UpdateMatchStatusRequest`

Implementation boundary:

- The frontend may validate required fields, non-negative integer scores, and
  duplicate team selection for fast feedback.
- The backend remains authoritative for authorization, team validity, match
  status transitions, prediction locking, bracket advancement, scoring,
  rescoring, provider normalization, and admin override behavior.
- If FE-006 discovers that an operation needs data not exposed by `docs/api.md`,
  it must document the dependency instead of inventing a production endpoint.

### FE-006 Test Expectations

UX-002 is documentation-only and has no automated test requirement. FE-006
should add component, route, and API-client tests covering:

- Admin route loading, empty, `403`, and API error states.
- Sync success, sync errors, and stale/not-synced display.
- Kickoff correction confirmation and validation behavior.
- Result confirmation, tied-score winner selection, and success feedback.
- Rescore confirmation and success/error feedback.
- Mobile rendering of match cards and accessible form labels/status messages.

## First Implementation Slice

1. Scaffold Next.js app with TypeScript and Tailwind.
2. Add API client and typed response models.
3. Implement OAuth login and callback.
4. Implement authenticated app shell.
5. Implement pool list, create, join, and selector.
6. Implement predictions by stage.
7. Implement rankings.
8. Implement profile.
9. Add smoke tests or component tests for critical flows.

## Implementation Notes

- Keep backend endpoints stable.
- Use `NEXT_PUBLIC_API_BASE_URL` for browser-visible backend calls and
  `API_BASE_URL` for server-side calls.
- Keep `FRONTEND_BASE_URL` available for OAuth callback validation.
