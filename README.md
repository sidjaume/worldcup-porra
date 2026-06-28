# World Cup Pool App

Private FIFA World Cup 2026 knockout prediction pool application.

The backend is implemented with FastAPI and PostgreSQL. The frontend is implemented with Next.js, React, TypeScript, and Tailwind CSS, and communicates with the backend through the REST API.

## Local Development

Install dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Configure `.env` from `.env.example`, then run migrations and seed development data:

```powershell
python -m alembic upgrade head
python -m scripts.seed_dev_data
```

Start the backend:

```powershell
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Docker Development

Start PostgreSQL, the FastAPI backend, and the Next.js frontend:

```powershell
docker compose up --build
```

Compose runs Alembic migrations before the backend starts. Seed demo data in
another terminal when needed:

```powershell
docker compose exec backend python -m scripts.seed_dev_data
```

Deployment and environment details are documented in `docs/deployment.md`,
`docs/infrastructure.md`, and `docs/environment.md`.

## Google OAuth Local Setup

For local login, configure the Google OAuth client as a **Web application** and add this exact authorized redirect URI:

```text
http://localhost:8000/api/v1/auth/google/callback
```

The value must exactly match `GOOGLE_REDIRECT_URI` in `.env`, including protocol, host, port, path, and trailing slash behavior. If you use `127.0.0.1` instead of `localhost`, update both `.env` and Google Cloud Console to the same value.

After changing `.env`, restart the backend process.
