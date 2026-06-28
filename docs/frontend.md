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
- Backend validation errors must be visible near the relevant action.
- Rankings must be easy to scan on mobile and desktop.
- Profile edits should be minimal and focused.

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
