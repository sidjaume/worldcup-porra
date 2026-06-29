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
| `TOURNAMENT_PROVIDER_BASE_URL` | No | `https://worldcup26.ir/get` | Base URL for the configured knockout data provider or self-hosted equivalent. |
| `TOURNAMENT_PROVIDER_API_KEY` | No | `...` | Optional provider key; leave empty for sources that do not require a key. |
| `TOURNAMENT_PROVIDER_TIMEOUT_SECONDS` | No | `10` | HTTP timeout for provider sync calls. |
| `TOURNAMENT_SYNC_TOURNAMENT_ID` | Required for scheduled sync | `00000000-0000-0000-0000-000000000000` | Internal tournament UUID passed to the sync job. |
| `TOURNAMENT_SYNC_YEAR` | No | `2026` | Tournament year passed to the sync job. |
| `TOURNAMENT_SYNC_MODE` | No | `all` | Sync job mode: `all`, `teams`, `matches`, or `results`. |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity. |

## Frontend Variables

Next.js frontend:

| Variable | Required | Example | Notes |
| --- | --- | --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Yes | `https://api.example.com` | Browser-visible backend URL. |
| `API_BASE_URL` | Yes | `https://api.example.com` | Server-side backend URL used by Next.js server components and routes. In Docker Compose this is `http://backend:8000`. |
| `FRONTEND_BASE_URL` | Yes | `https://app.example.com` | Public frontend URL used for OAuth redirect construction. |

## Windows Node/NPM PATH

If Node.js is installed but `node` or `npm` are not visible from the project
PowerShell session, the terminal likely started before the Windows PATH update
was inherited. For this repository, use this prefix before frontend commands:

```powershell
$env:Path = 'C:\Program Files\nodejs;' + "$env:APPDATA\npm;" + $env:Path
```

Run NPM through `npm.cmd`:

```powershell
cd frontend
npm.cmd run lint
npm.cmd test
npm.cmd run typecheck
npm.cmd run build
```

Use `npm.cmd` instead of bare `npm` because PowerShell may resolve `npm.ps1`
first and block it when script execution is disabled.

## Local `.env`

Use `.env.example` as the template:

```powershell
Copy-Item .env.example .env
```

For local Google OAuth, use this exact redirect URI:

```text
http://localhost:8000/api/v1/auth/google/callback
```

This is the FastAPI backend callback. The Next.js frontend still runs at
`http://localhost:3000`, and `FRONTEND_BASE_URL` plus `ALLOWED_ORIGINS` should
use that frontend origin locally.

If you use `127.0.0.1`, update both `.env` and Google Cloud Console.

In production, `ENVIRONMENT=production` requires explicit values for
`DATABASE_URL`, OAuth credentials, `SECRET_KEY`, `GOOGLE_REDIRECT_URI`,
`FRONTEND_BASE_URL`, `BACKEND_BASE_URL`, and `ALLOWED_ORIGINS`. Localhost
URLs are rejected for production settings.

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
