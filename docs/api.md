# API Design

Status: Implemented MVP API surface exists and is pending contract review.
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
- `/admin`: match creation, match completion, and rescoring.
- `/health`: unauthenticated process/database health endpoint outside `/api/v1`.

The Next.js frontend API client currently calls the documented `/api/v1`
surfaces. This does not replace the need for Reviewer validation of auth,
authorization, validation, accessibility, and error behavior.

## Contract Reconciliation Gaps

The following differences were observed during ORCH-001 and need specialist
follow-up rather than silent code changes:

- `PATCH /api/v1/pools/{pool_id}`: implemented response model is `PoolDetail` and does not include `is_active`; the example below includes `is_active`. Architect/Backend should decide whether to add `is_active` to `PoolDetail` or narrow the documented response.
- `PATCH /api/v1/admin/matches/{match_id}`: implemented behavior completes a match by accepting `home_score`, `away_score`, and `winner_team_id`; the contract text says it can also update schedule, teams, and status. Backend should either add the broader update behavior or the contract should be narrowed to a completion endpoint.
- `POST /api/v1/admin/matches/{match_id}/rescore`: implemented response is `MatchRead`. Contract should explicitly document this response if accepted.
- Rankings: implementation tie-breaks by total points, exact scores, correct winners, then display name. `docs/database.md` recommends earliest joined participant as the final tie-breaker. Backend/Architect should choose one deterministic rule.
- OAuth redirect configuration: the backend-owned callback should be `BACKEND_BASE_URL/api/v1/auth/google/callback`; `.env.example` currently disagrees with Docker Compose. DevOps/Backend should align environment examples and deployment docs.
- Error format is implemented for service/domain errors and unauthorized cases; FastAPI/Pydantic `422` validation errors still use FastAPI's default shape unless a custom handler is added. Reviewer/Backend should decide whether full standardization is required for MVP.

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
  "invite_code": "ABCD-1234"
}
```

The invite code is returned only on creation or rotation.

### GET `/api/v1/pools/{pool_id}`

Returns pool details for members.

Response:

```json
{
  "id": "uuid",
  "name": "Office Pool",
  "tournament_id": "uuid",
  "owner_user_id": "uuid",
  "participant_count": 12,
  "created_at": "2026-06-28T17:00:00Z"
}
```

### PATCH `/api/v1/pools/{pool_id}`

Owner-only pool update.

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

Current implementation note: this endpoint currently returns the `PoolDetail`
shape (`id`, `name`, `tournament_id`, `owner_user_id`, `participant_count`,
`created_at`) and omits `is_active`. This is an open contract gap.

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

Lists active participants. Members can view.

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
    "winner_team_id": null
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
  "predicted_away_goals": 1
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

Updates schedule, teams, status, or scores. Admin-only.

Current implementation note: this endpoint currently completes a match only,
using:

```json
{
  "home_score": 2,
  "away_score": 1,
  "winner_team_id": "uuid"
}
```

It returns `MatchRead`, advances the winner when configured, and scores
predictions for that match.

When a match is marked completed, the backend should:

1. Validate scores and winner.
2. Advance the winner to the next match slot if configured.
3. Score predictions for that match.

### POST `/api/v1/admin/matches/{match_id}/rescore`

Recalculates scores for a completed match. Admin-only.

Current implementation response: `MatchRead`.

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
