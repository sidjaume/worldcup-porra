# AI Agent Instructions

## Role

Act as a Senior Full Stack Engineer specialized in Python web applications, software architecture and production-quality development.

You are responsible for:

- Architecture decisions.
- Code quality.
- Security.
- Maintainability.
- Scalability.

Think and work as the technical owner of the project.

---

# Project Goal

Build a modern, maintainable and scalable web application for managing a private FIFA World Cup 2026 prediction pool ("porra").

The application allows a group of users to compete by predicting knockout stage match results.

The group stage is already completed.

The application only manages:

- Round of 32.
- Round of 16.
- Quarter-finals.
- Semi-finals.
- Final.

The system must NOT manage:

- Group stage predictions.
- Group standings.
- Qualification rules.

Users should be able to:

- Create private prediction pools.
- Join pools using invitation codes.
- Predict match results.
- Track accumulated points.
- Compare rankings against participants.

The initial target is small private groups (10-100 users), but the architecture should support future growth.

---

# MVP Scope

The MVP includes:

## Authentication

- User registration.
- Authentication using Google OAuth 2.0.
- User profile management.

---

## Prediction Pools

- Create pools.
- Join pools.
- Manage participants.
- Generate invitation codes.

---

## Tournament

Support knockout bracket management:

- Round of 32.
- Round of 16.
- Quarter-finals.
- Semi-finals.
- Final.

A match must support:

- Home team.
- Away team.
- Tournament stage.
- Scheduled date.
- Status.
- Final score.
- Winner.

The system must understand knockout progression:

- Winner advances to next stage.
- Matches belong to a tournament bracket.

---

## Predictions

Users can:

- Submit predictions before the match starts.
- Edit predictions until match lock time.
- View previous predictions.

Predictions must contain:

- User.
- Match.
- Predicted home goals.
- Predicted away goals.
- Submission timestamp.
- Lock status.

Predictions are not allowed after the match begins.

---

# Scoring System

The scoring engine calculates points independently from UI and persistence.

Rules:

## Correct Winner

+2 points if the predicted winning team is correct.

---

## Exact Score

+2 additional points if both goals are exactly correct.

Example:

Prediction:

Spain 3 - 1 Austria

Actual:

Spain 3 - 1 Austria

Points:

- Correct winner: +2
- Exact score: +2

Total: +4

---

## Partial Score

+1 additional point if one team's goal count is correct.

Example:

Prediction:

Spain 3 - 1 Austria

Actual:

Spain 3 - 0 Austria

Points:

- Correct winner: +2
- Spain goals correct: +1

Total: +3

---

The scoring logic must be:

- Independent.
- Testable.
- Configurable.

Future scoring rules should not require rewriting the application.

---

# Architecture Guidelines

Use a modular monolith architecture.

Recommended structure:

```
app/
├── api/
├── frontend/
├── domain/
├── services/
├── repositories/
├── models/
├── config/
└── tests/
```


Business rules must not depend on:

- Streamlit.
- FastAPI.
- Database.
- External providers.

The domain layer must be independently testable.

---

# Tech Stack

## Frontend

Use:

- Streamlit

Rules:

- Keep components reusable.
- Avoid business logic inside UI.
- Keep pages small.
- Communicate with backend through APIs.

---

## Backend

Use:

- Python
- FastAPI

Requirements:

- REST API.
- Request validation.
- Error handling.
- Authentication middleware.
- Clear separation of responsibilities.

---

## Database

Use:

- PostgreSQL

Database will be hosted using:

- Neon PostgreSQL.

The database must support:

- Users.
- Pools.
- Participants.
- Teams.
- Matches.
- Predictions.
- Scores.
- Rankings.

---

# Database Rules

Follow:

- Use PostgreSQL migrations.
- Never modify schemas manually.
- Use constraints.
- Add indexes when needed.
- Keep database access isolated.
- Use repositories.

Database changes must be reproducible.

---

# Deployment Architecture

The application must be deployable to a cloud environment.

Target deployment:

## Frontend

Platform:

- Render

Runs:

- Streamlit application.

---

## Backend

Platform:

- Render

Runs:

- FastAPI service.

Requirements:

- Production ASGI server.
- Health check endpoint.
- Environment-based configuration.

---

## Database

Platform:

- Neon

Runs:

- Managed PostgreSQL.

The application must:

- Never depend on local database files.
- Use connection strings.
- Support production database migrations.

---

# Deployment Requirements

The project must support:

- Docker deployment.
- Environment variables.
- Development and production configurations.

Never store:

- Secrets.
- API keys.
- Passwords.

inside the repository.

---

Required environment variables:

Example:
```
DATABASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SECRET_KEY=
ENVIRONMENT=
```

---

# Coding Standards

Python:

- Follow PEP8.
- Use type hints.
- Use clear naming.
- Write modular code.

General:

- Avoid duplication.
- Keep functions focused.
- Add validation.
- Handle errors properly.
- Write maintainable code.

---

# Development Workflow

Before coding:

1. Analyze the task.
2. Identify affected modules.
3. Explain the approach.

For small changes:

- Implement directly.

For large changes:

- Provide a short plan first.

After changes:

Summarize:

- Files changed.
- Implementation details.
- Tests executed.
- Possible improvements.

---

# Product Constraints

This is an MVP-first project.

Avoid:

- Microservices.
- Over-engineering.
- Complex infrastructure.
- Premature abstractions.

Prefer:

- Simple solutions.
- Modular monolith.
- Clear boundaries.
- Maintainable code.
- Cloud-ready architecture.

---

# Do Not

Do not:

- Put business logic inside Streamlit.
- Introduce dependencies without reason.
- Rewrite working code unnecessarily.
- Create abstractions without a real use case.
- Ignore existing project conventions.
- Depend on local filesystem persistence.