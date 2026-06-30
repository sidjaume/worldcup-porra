# API Design

Status: Implemented MVP API surface reconciled; targeted contract decisions applied.
Last reconciled: 2026-06-29.

This file is the intended API contract plus reconciliation notes for the API
surface currently implemented under `app/api`. Frontend and backend work must
not introduce further divergence without Architect review.

## API Principles

- REST JSON API under `/api/v1`.
- Backend owns authentication, authorization, validation, scoring, and persistence.
- The frontend calls the backend only through these APIs.
- All protected endpoints require an `Authorization: Bearer <access_token>` header.
- All timestamps are ISO 8601 UTC.
- Request and response bodies use snake_case to match Python models.

## Contract Ownership

The architect owns this API contract. Frontend and backend agents must treat this file as the shared source of truth.

Contract changes require:

1. Update this document first.
2. Review the impact on frontend, backend, database, authentication, and deployment.
3. Implement backend changes.
4. Update frontend API client and types.
5. Add or update tests for affected flows.

## Current Implementation Snapshot

The repository currently implements these route groups under `/api/v1`:

- `/auth`: Google OAuth start/callback, exchange, refresh, logout.
- `/users`: current profile read/update.
- `/pools`: pool list/create/detail/update/join, participants, participant removal, invite-code rotation.
- `/tournaments`: tournament list, team list, match list.
- `/pools/{pool_id}/predictions`: current user's predictions and match prediction visibility.
- `/pools/{pool_id}/rankings`: aggregate rankings.
- `/admin`: match creation, match completion, kickoff correction, provider sync,
  and rescoring.
- `/health`: unauthenticated process/database health endpoint outside `/api/v1`.

The Next.js frontend API client currently calls the documented `/api/v1`
surfaces. This does not replace the need for Reviewer validation of auth,
authorization, validation, accessibility, and error behavior.

## Contract Reconciliation Notes

The ARCH-002 decisions are reflected in this contract:

- `PATCH /api/v1/admin/matches/{match_id}` is a match-completion endpoint only.
- `POST /api/v1/admin/matches/{match_id}/rescore` returns `MatchRead`.
- Rankings are ordered by total points descending, exact scores descending, correct winners descending, then earliest active participant join time ascending.

The ARCH-004 decisions extend this contract:

- Predictions include `predicted_winner_team_id` only for tied-score advancing-winner semantics.
- Existing-match admin team correction and status correction are separate command endpoints.
- Provider sync must preserve manual overrides and fail closed on unknown provider statuses.
- Render cron is optional for operations; the API contract is the same whether sync is admin-triggered, locally scheduled, or cron-triggered.

Error format is implemented for service/domain errors, unauthorized cases, and FastAPI/Pydantic `422` request validation errors.

## Frontend/Backend Contract Rules

- Frontend must not infer business rules that the backend can validate.
- Backend must validate every protected operation even if the frontend hides controls.
- Frontend must handle `401` by refreshing tokens when possible, then redirecting to login if refresh fails.
- Backend must use the standard error body for expected errors.
- Backend must return `404` for resources that are missing or not visible to the current user when revealing existence would be inappropriate.
- Pagination is not required for MVP pool sizes, but list endpoints should be designed so pagination can be added later without changing resource names.

## Common Responses

### Error Body

```json
{
  "error": {
    "code": "prediction_locked",
    "message": "Predictions are closed for this match.",
    "details": {}
  }
}
```

### Common Status Codes

- `200 OK`: Successful read or update.
- `201 Created`: Resource created.
- `204 No Content`: Successful delete/logout action.
- `400 Bad Request`: Invalid operation.
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Authenticated but not allowed.
- `404 Not Found`: Resource not found or not visible to user.
- `409 Conflict`: Duplicate membership, duplicate prediction, stale state, or invite collision.
- `422 Unprocessable Entity`: Request validation error.

## Health

### GET `/health`

Unauthenticated health endpoint for Render.

Response:

```json
{
  "status": "ok",
  "database": "ok"
}
```

The endpoint should return a non-2xx response if operation-critical dependencies fail.

## Authentication

The backend owns Google OAuth 2.0. The frontend never receives Google client secrets.

### GET `/api/v1/auth/google/start`

Starts Google OAuth.

Query parameters:

- `redirect_uri`: Frontend callback URL to return to after successful login.

Response:

- `302 Found` redirect to Google authorization URL.

Backend actions:

- Generate OAuth `state`.
- Store state server-side or in signed short-lived state data.
- Redirect to Google with configured client ID, callback URL, scopes, and state.

### GET `/api/v1/auth/google/callback`

Google OAuth callback.

Query parameters:

- `code`
- `state`

Response:

- `302 Found` redirect to frontend callback with a one-time application exchange code.

Backend actions:

- Validate `state`.
- Exchange Google authorization code for Google tokens.
- Fetch/validate Google identity.
- Upsert `users` and `oauth_accounts`.
- Create a short-lived one-time `auth_exchange_code`.
- Redirect to `redirect_uri?code=<one_time_code>`.

### POST `/api/v1/auth/exchange`

Exchanges a one-time application code for application tokens.

Request:

```json
{
  "code": "one-time-code-from-callback"
}
```

Response:

```json
{
  "access_token": "jwt",
  "refresh_token": "opaque-refresh-token",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "User Name",
    "avatar_url": "https://example.com/avatar.png"
  }
}
```

### POST `/api/v1/auth/refresh`

Rotates a refresh token and returns a new access token.

Request:

```json
{
  "refresh_token": "opaque-refresh-token"
}
```

Response:

```json
{
  "access_token": "jwt",
  "refresh_token": "new-opaque-refresh-token",
  "token_type": "bearer",
  "expires_in": 900
}
```

### POST `/api/v1/auth/logout`

Revokes the current refresh token/session.

Request:

```json
{
  "refresh_token": "opaque-refresh-token"
}
```

Response:

- `204 No Content`

## Users

### GET `/api/v1/users/me`

Returns the authenticated profile.

Response:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "User Name",
  "avatar_url": "https://example.com/avatar.png"
}
```

### PATCH `/api/v1/users/me`

Updates editable profile fields.

Request:

```json
{
  "display_name": "Updated Name"
}
```

Response:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "Updated Name",
  "avatar_url": "https://example.com/avatar.png"
}
```

## Pools

### GET `/api/v1/pools`

Lists pools where the current user is an active participant.

Response:

```json
[
  {
    "id": "uuid",
    "name": "Office Pool",
    "tournament_id": "uuid",
    "role": "owner",
    "participant_count": 12,
    "created_at": "2026-06-28T17:00:00Z"
  }
]
```

### POST `/api/v1/pools`

Creates a pool and adds the creator as owner.

Request:

```json
{
  "name": "Office Pool",
  "tournament_id": "uuid"
}
```

Response:

```json
{
  "id": "uuid",
  "name": "Office Pool",
  "tournament_id": "uuid",
  "role": "owner",
  "participant_count": 1,
  "created_at": "2026-06-28T17:00:00Z",
  "invite_code": "ABCD-1234"
}
```

The invite code is returned only on creation or rotation.

### GET `/api/v1/pools/{pool_id}`

Returns pool details for active member pools. Inactive pools are rejected for normal member access.

Response:

```json
{
  "id": "uuid",
  "name": "Office Pool",
  "tournament_id": "uuid",
  "owner_user_id": "uuid",
  "is_active": true,
  "participant_count": 12,
  "created_at": "2026-06-28T17:00:00Z"
}
```

### PATCH `/api/v1/pools/{pool_id}`

Owner-only pool update. Owners can update inactive pools through this endpoint, including reactivating them by setting `is_active` to `true`.

Request:

```json
{
  "name": "Updated Pool Name",
  "is_active": true
}
```

Response:

```json
{
  "id": "uuid",
  "name": "Updated Pool Name",
  "is_active": true
}
```

### POST `/api/v1/pools/join`

Joins a pool by invite code.

Request:

```json
{
  "invite_code": "ABCD-1234"
}
```

Response:

```json
{
  "pool_id": "uuid",
  "name": "Office Pool",
  "role": "participant"
}
```

### POST `/api/v1/pools/{pool_id}/invite-code/rotate`

Owner-only invite code rotation.

Response:

```json
{
  "invite_code": "WXYZ-9876",
  "rotated_at": "2026-06-28T17:00:00Z"
}
```

## Participants

### GET `/api/v1/pools/{pool_id}/participants`

Lists active participants for active member pools. Inactive pools are rejected for normal member access.

Response:

```json
[
  {
    "user_id": "uuid",
    "display_name": "User Name",
    "role": "participant",
    "joined_at": "2026-06-28T17:00:00Z"
  }
]
```

### DELETE `/api/v1/pools/{pool_id}/participants/{user_id}`

Owner-only removal. Owners cannot remove themselves unless ownership is transferred or the pool is deactivated.

Response:

- `204 No Content`

## Tournament

### GET `/api/v1/tournaments`

Lists available tournaments.

Response:

```json
[
  {
    "id": "uuid",
    "name": "FIFA World Cup 2026",
    "year": 2026,
    "is_active": true
  }
]
```

### GET `/api/v1/tournaments/{tournament_id}/teams`

Lists tournament teams.

Response:

```json
[
  {
    "id": "uuid",
    "name": "Spain",
    "short_name": "ESP",
    "fifa_code": "ESP",
    "flag_url": null
  }
]
```

### GET `/api/v1/tournaments/{tournament_id}/matches`

Lists matches, optionally filtered by stage.

Query parameters:

- `stage`: Optional stage enum.

Response:

```json
[
  {
    "id": "uuid",
    "stage": "round_of_32",
    "bracket_position": 1,
    "home_team": {
      "id": "uuid",
      "name": "Spain"
    },
    "away_team": {
      "id": "uuid",
      "name": "Austria"
    },
    "scheduled_at": "2026-06-28T19:00:00Z",
    "status": "scheduled",
    "home_score": null,
    "away_score": null,
    "winner_team_id": null,
    "sync_source": null,
    "admin_override": false,
    "provider_last_synced_at": null
  }
]
```

## Predictions

### GET `/api/v1/pools/{pool_id}/predictions`

Lists the current user's predictions in a pool, optionally filtered by match or stage.

Query parameters:

- `match_id`: Optional UUID.
- `stage`: Optional stage enum.

Response:

```json
[
  {
    "id": "uuid",
    "match_id": "uuid",
    "predicted_home_goals": 3,
    "predicted_away_goals": 1,
    "predicted_winner_team_id": null,
    "status": "editable",
    "submitted_at": "2026-06-28T17:00:00Z",
    "updated_at": "2026-06-28T17:00:00Z",
    "score": null
  }
]
```

### PUT `/api/v1/pools/{pool_id}/matches/{match_id}/prediction`

Creates or updates the current user's prediction for a match. This endpoint is idempotent before lock time.

Request:

```json
{
  "predicted_home_goals": 3,
  "predicted_away_goals": 1,
  "predicted_winner_team_id": null
}
```

Response:

```json
{
  "id": "uuid",
  "pool_id": "uuid",
  "match_id": "uuid",
  "predicted_home_goals": 3,
  "predicted_away_goals": 1,
  "predicted_winner_team_id": null,
  "status": "editable",
  "submitted_at": "2026-06-28T17:00:00Z",
  "updated_at": "2026-06-28T17:00:00Z"
}
```

Validation:

- User must be an active pool participant.
- Match must belong to the pool tournament.
- Match must be scheduled.
- Current server time must be before lock time.
- Goal counts must be non-negative integers.
- If `predicted_home_goals == predicted_away_goals`, `predicted_winner_team_id`
  is required and must match the home or away team for the match.
- If predicted goals are not tied, `predicted_winner_team_id` must be omitted or
  `null`; the predicted winner is derived from the goals.
- Tied predictions are rejected while either match team is unknown.

Example tied prediction:

```json
{
  "predicted_home_goals": 1,
  "predicted_away_goals": 1,
  "predicted_winner_team_id": "uuid-of-home-or-away-team"
}
```

### GET `/api/v1/pools/{pool_id}/matches/{match_id}/predictions`

Lists visible predictions for a match. For fairness, return all participants' predictions only after the match locks. Before lock, return only the current user's prediction.

Response:

```json
[
  {
    "user_id": "uuid",
    "display_name": "User Name",
    "predicted_home_goals": 3,
    "predicted_away_goals": 1,
    "predicted_winner_team_id": null,
    "submitted_at": "2026-06-28T17:00:00Z",
    "score": {
      "points": 4,
      "correct_winner": true,
      "exact_score": true
    }
  }
]
```

## Rankings

### GET `/api/v1/pools/{pool_id}/rankings`

Returns aggregate standings for the pool.

Ordering:

1. `total_points` descending.
2. `exact_scores` descending.
3. `correct_winners` descending.
4. Active participant `joined_at` ascending.

Response:

```json
[
  {
    "rank": 1,
    "user_id": "uuid",
    "display_name": "User Name",
    "total_points": 18,
    "exact_scores": 3,
    "correct_winners": 7,
    "predictions_scored": 8,
    "predictions_submitted": 12
  }
]
```

## Admin Endpoints

For MVP, admin endpoints can be protected by an environment-configured admin email list or a simple `is_admin` field added later.

### POST `/api/v1/admin/tournaments/{tournament_id}/matches`

Creates a match. Admin-only.

### PATCH `/api/v1/admin/matches/{match_id}`

Completes a match. Admin-only. This endpoint intentionally accepts only match
completion fields.

Request:

```json
{
  "home_score": 2,
  "away_score": 1,
  "winner_team_id": "uuid"
}
```

Response: `MatchRead`.

Completing a match advances the winner when configured and scores predictions
for that match. Penalty-decided matches must store the tied end-of-play score
and the advancing team as `winner_team_id`; penalty shoot-out goals are not
included in `home_score` or `away_score`.

When a match is marked completed, the backend should:

1. Validate scores and winner.
2. Advance the winner to the next match slot if configured.
3. Score predictions for that match.

### PATCH `/api/v1/admin/matches/{match_id}/kickoff`

Updates a non-completed match kickoff/lock time. Admin-only. This sets
`admin_override=true` so later provider sync runs do not silently undo the
manual correction.

Request:

```json
{
  "scheduled_at": "2026-06-28T19:00:00Z"
}
```

Response: `MatchRead`.

### PATCH `/api/v1/admin/matches/{match_id}/teams`

Corrects the teams assigned to an existing non-completed match. Admin-only.
This is a fallback for provider or seed mistakes and intentionally does not
complete the match, score predictions, or edit bracket linkage.

Request:

```json
{
  "home_team_id": "uuid-or-null",
  "away_team_id": "uuid-or-null"
}
```

Response: `MatchRead`.

Validation:

- At least one of `home_team_id` or `away_team_id` must be present.
- Match must not be completed.
- Each non-null team must belong to the match tournament.
- If both teams are present, they must be distinct.
- The backend sets `sync_source="admin"` and `admin_override=true`.

### PATCH `/api/v1/admin/matches/{match_id}/status`

Corrects operational status for an existing non-completed match. Admin-only.

Request:

```json
{
  "status": "in_progress"
}
```

Response: `MatchRead`.

Validation:

- Accepted values: `scheduled`, `locked`, `in_progress`, `cancelled`.
- `completed` is rejected here; use `PATCH /api/v1/admin/matches/{match_id}`
  with result fields to complete a match.
- Completed matches cannot be reopened through this MVP endpoint.
- The endpoint does not change teams, kickoff time, scores, winner, scoring, or
  bracket linkage.
- The backend sets `sync_source="admin"` and `admin_override=true`.

### POST `/api/v1/admin/matches/{match_id}/rescore`

Recalculates scores for a completed match. Admin-only.

Response: `MatchRead`.

### POST `/api/v1/admin/tournaments/{tournament_id}/sync`

Runs the configured provider adapter for an admin-triggered sync. Admin-only.
The backend imports provider teams, imports or updates knockout fixtures, then
syncs in-progress/completed results. Sync is idempotent: rerunning it must not
duplicate teams, matches, prediction scores, or bracket progression.

Manual overrides take precedence over provider data. Provider sync must not
mutate provider-managed fields on matches with `admin_override=true`, and
provider-driven bracket progression must not replace a populated downstream
slot with a different team. Such rows should be reported in `errors` rather
than silently overwritten.

Provider normalization fails closed: unknown provider statuses, missing
completed-result scores, or missing advancing winners produce sync errors and
must not default to scheduled. Numeric zero is a valid score and must be
preserved.

Request:

```json
{
  "year": 2026
}
```

Response:

```json
{
  "teams_created": 0,
  "teams_updated": 0,
  "matches_created": 0,
  "matches_updated": 0,
  "errors": []
}
```

## Authentication Flow

1. User clicks "Sign in with Google" in the frontend.
2. The frontend redirects the browser to `/api/v1/auth/google/start?redirect_uri=<frontend_callback>`.
3. Backend redirects to Google with OAuth state.
4. Google redirects to backend `/api/v1/auth/google/callback`.
5. Backend validates Google identity and upserts the application user.
6. Backend creates a short-lived one-time exchange code.
7. Backend redirects the browser to the frontend callback with that exchange code.
8. The frontend exchanges the code through `/api/v1/auth/exchange`.
9. Backend returns application access and refresh tokens.
10. The frontend stores auth state and sends the access token on API calls.
11. The frontend refreshes the access token through `/api/v1/auth/refresh` when needed.
12. Logout calls `/api/v1/auth/logout` and clears frontend auth state.

For the target Next.js frontend, prefer storing refresh tokens in an HTTP-only session cookie managed by a server route. The backend API contract does not require Google client secrets in the frontend.

## Token Policy

Recommended MVP defaults:

- Access token lifetime: 15 minutes.
- Refresh token lifetime: 14-30 days.
- Refresh tokens are opaque random values stored only as hashes.
- Refresh tokens rotate on use.
- Access tokens are signed with `SECRET_KEY`.
- Token payload includes `sub`, `email`, `display_name`, `iat`, `exp`, and `jti`.
