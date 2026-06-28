# Environment Variables

Environment variables are the only supported configuration mechanism outside
local defaults. Never commit real secrets.

## Backend Variables

| Variable | Required | Example | Notes |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql+psycopg://user:pass@host/db` | Neon in production, Docker PostgreSQL locally. |
| `GOOGLE_CLIENT_ID` | Yes in auth-enabled envs | `...apps.googleusercontent.com` | Google OAuth client ID. |
| `GOOGLE_CLIENT_SECRET` | Yes in auth-enabled envs | `...` | Secret value. |
| `GOOGLE_REDIRECT_URI` | Yes in auth-enabled envs | `https://api.example.com/api/v1/auth/google/callback` | Must exactly match Google Cloud Console. |
| `SECRET_KEY` | Yes | generated random string | Used for JWT signing. |
| `ENVIRONMENT` | Yes | `development`, `test`, `production` | Production validates required secrets. |
| `FRONTEND_BASE_URL` | Yes | `https://app.example.com` | Used for OAuth redirects. |
| `BACKEND_BASE_URL` | Yes | `https://api.example.com` | Public backend URL. |
| `ALLOWED_ORIGINS` | Yes | `https://app.example.com` | Comma-separated CORS origins. |
| `ADMIN_EMAILS` | No | `admin@example.com` | Comma-separated initial admin emails. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | JWT access token lifetime. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `30` | Refresh token lifetime. |
| `SCORING_VERSION` | No | `mvp-2026-v1` | Version label for scoring rules. |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity. |

## Frontend Variables

Next.js frontend:

| Variable | Required | Example | Notes |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | `https://api.example.com` | Browser-visible backend URL. |
| `API_BASE_URL` | Yes | `https://api.example.com` | Server-side backend URL used by Next.js server components and routes. In Docker Compose this is `http://backend:8000`. |
| `FRONTEND_BASE_URL` | Yes | `https://app.example.com` | Public frontend URL used for OAuth redirect construction. |

## Local `.env`

Use `.env.example` as the template:

```powershell
Copy-Item .env.example .env
```

For local Google OAuth, use this exact redirect URI:

```text
http://localhost:8000/api/v1/auth/google/callback
```

If you use `127.0.0.1`, update both `.env` and Google Cloud Console.

## Production Secret Generation

Generate `SECRET_KEY` locally and paste it into Render:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Do not place production secrets in `.env.example`, `render.yaml`, docs, commits,
or issue comments.

## Render Mapping

Set backend variables on `worldcup-pool-api` and frontend variables on
`worldcup-pool-frontend`.

Do not set `DATABASE_URL`, `GOOGLE_CLIENT_SECRET`, or `SECRET_KEY` on the
frontend service.
