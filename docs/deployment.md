# Deployment Guide

This project deploys as a modular monolith with separate web services for the
FastAPI backend and the frontend. PostgreSQL is provided by Neon.

## Production Targets

- Backend: Render web service using `Dockerfile.backend`.
- Frontend: Render web service using `Dockerfile.frontend`, running the Next.js
  production server.
- Database: Neon PostgreSQL.
- CI: GitHub Actions in `.github/workflows/ci.yml`.

## Render Blueprint

The repository includes `render.yaml` for both web services.

### Backend

Render runs:

- Build: Docker image from `Dockerfile.backend`.
- Pre-deploy: `python -m alembic upgrade head`.
- Start: the Docker `CMD`, which runs Uvicorn on Render's injected `PORT`.
- Health check: `GET /health`.

Required Render environment variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `FRONTEND_BASE_URL`
- `BACKEND_BASE_URL`
- `ALLOWED_ORIGINS`
- `ADMIN_EMAILS`

Use Render secret/synced environment values for every secret. Do not commit
production values to the repository.

### Frontend

Render runs:

- Build: Docker image from `Dockerfile.frontend`.
- Start: the Docker `CMD`, which runs the Next.js standalone server on Render's
  injected `PORT`.
- Health check: `GET /health`.

Required Render environment variables:

- `NEXT_PUBLIC_API_BASE_URL`: browser-visible public backend URL, for example
  `https://worldcup-pool-api.onrender.com`.
- `API_BASE_URL`: server-side backend URL. In production this can match
  `NEXT_PUBLIC_API_BASE_URL`; in Docker Compose it points at `http://backend:8000`.
- `FRONTEND_BASE_URL`: public frontend URL, for example
  `https://worldcup-pool-frontend.onrender.com`.

The backend `FRONTEND_BASE_URL` and `ALLOWED_ORIGINS` values must match the
frontend public URL.

## Neon

Create a Neon PostgreSQL project and copy its connection string into Render as
`DATABASE_URL`.

The application accepts either of these URL forms:

- `postgresql://...`
- `postgresql+psycopg://...`

At runtime, settings normalize `postgresql://` into the SQLAlchemy psycopg
driver format.

## Google OAuth

Create a Google OAuth client of type `Web application`.

Authorized redirect URI for production:

```text
https://<backend-render-host>/api/v1/auth/google/callback
```

Then configure:

- `GOOGLE_REDIRECT_URI` with the same backend callback URL.
- `BACKEND_BASE_URL` with the public backend URL.
- `FRONTEND_BASE_URL` with the public frontend URL.
- `ALLOWED_ORIGINS` with the public frontend URL.

The redirect URI must match exactly in Google Cloud Console and Render.
When `ENVIRONMENT=production`, backend startup requires these values to be set
explicitly and rejects localhost URLs.

## Local Docker

Start the stack:

```powershell
docker compose up --build
```

The `migrate` Compose service runs Alembic before the backend starts.

Seed development data:

```powershell
docker compose exec backend python -m scripts.seed_dev_data
```

Open:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- Backend health check: `http://localhost:8000/health`
- Frontend health check: `http://localhost:3000/health`

## Release Checklist

1. GitHub Actions passes.
2. Render environment variables are configured.
3. Neon database is reachable from Render.
4. `API_BASE_URL`, `FRONTEND_BASE_URL`, and `ALLOWED_ORIGINS` use deployed
   HTTPS URLs.
5. Google OAuth redirect URI matches the deployed backend callback.
6. Render pre-deploy migration succeeds.
7. Backend `/health` returns `{"status": "ok", "database": "ok"}`.
8. Frontend `/health` returns a 2xx status.
