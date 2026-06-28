# API Design

## API Principles

- REST JSON API under `/api/v1`.
- Backend owns authentication, authorization, validation, scoring, and persistence.
- Streamlit frontend calls the backend only through these APIs.
- All protected endpoints require an `Authorization: Bearer <access_token>` header.
- All timestamps are ISO 8601 UTC.
- Request and response bodies use snake_case to match Python models.

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

When a match is marked completed, the backend should:

1. Validate scores and winner.
2. Advance the winner to the next match slot if configured.
3. Score predictions for that match.

### POST `/api/v1/admin/matches/{match_id}/rescore`

Recalculates scores for a completed match. Admin-only.

## Authentication Flow

1. User clicks "Sign in with Google" in Streamlit.
2. Streamlit redirects the browser to `/api/v1/auth/google/start?redirect_uri=<frontend_callback>`.
3. Backend redirects to Google with OAuth state.
4. Google redirects to backend `/api/v1/auth/google/callback`.
5. Backend validates Google identity and upserts the application user.
6. Backend creates a short-lived one-time exchange code.
7. Backend redirects the browser to the Streamlit callback with that exchange code.
8. Streamlit calls `/api/v1/auth/exchange` from the server side.
9. Backend returns application access and refresh tokens.
10. Streamlit stores tokens in session state and sends access token on API calls.
11. Streamlit refreshes the access token through `/api/v1/auth/refresh` when needed.
12. Logout calls `/api/v1/auth/logout` and clears Streamlit session state.

## Token Policy

Recommended MVP defaults:

- Access token lifetime: 15 minutes.
- Refresh token lifetime: 14-30 days.
- Refresh tokens are opaque random values stored only as hashes.
- Refresh tokens rotate on use.
- Access tokens are signed with `SECRET_KEY`.
- Token payload includes `sub`, `email`, `display_name`, `iat`, `exp`, and `jti`.

