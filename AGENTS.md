# AI Multi-Agent Project Instructions

## Project Overview

This project is developed collaboratively by multiple AI agents.

Every agent must read this document before performing any task.

This file is the single source of truth for:

- Project vision
- Technical goals
- Architectural principles
- Development philosophy
- Technology stack
- Collaboration rules

Detailed implementation instructions belong to each specialized agent.

---

# Project Goal

Build a modern web application for managing a private FIFA World Cup 2026 prediction pool ("Porra").

The application must provide a polished user experience while remaining simple to maintain and inexpensive to operate.

The application targets private groups of approximately 10–100 users.

---

# Tournament Scope

The application only manages the knockout phase.

Supported stages:

- Round of 32
- Round of 16
- Quarter-finals
- Semi-finals
- Final

The application does NOT manage:

- Group stage
- Qualification rules
- League standings

---

# Core Features

The MVP includes:

- Google authentication
- Private prediction pools
- Invitation codes
- Match predictions
- Prediction locking
- Automatic scoring
- Live rankings

---

# Scoring Rules

Winner correctly predicted

+2 points

Exact score

+2 additional points

One team's goals correctly predicted

+1 additional point

Maximum score per match:

4 points

The scoring engine must remain configurable.

---

# Technical Stack

Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

Backend

- FastAPI
- Python

Database

- PostgreSQL
- Neon

Authentication

- Google OAuth 2.0

Hosting

- Render

Version Control

- GitHub

Infrastructure

- Docker
- GitHub Actions

---

# Architecture

The project follows a Modular Monolith architecture.

Layers:

Presentation

↓

API

↓

Application Services

↓

Domain

↓

Repositories

↓

Database

Business rules belong exclusively to the Domain layer.

---

# Project Principles

Always prioritize:

- Simplicity
- Maintainability
- Readability
- Testability
- Security

Avoid unnecessary complexity.

---

# AI Agent Responsibilities

The project contains multiple specialized agents.

## Architect

Owns:

- Architecture
- Technical decisions
- API contracts
- Domain model

---

## Backend

Owns:

- FastAPI
- Business rules
- Authentication
- Database
- Scoring engine

---

## Frontend

Owns:

- Next.js
- UI
- UX
- API consumption

---

## DevOps

Owns:

- Docker
- Deployment
- CI/CD
- Render
- Neon
- Environment variables

---

## Reviewer

Owns:

- Code quality
- Reviews
- Testing validation
- Production readiness

---

# Collaboration Rules

Agents must never invade another agent's responsibilities.

When functionality depends on another layer:

Document the dependency.

Do not implement another team's work.

---

# Coding Philosophy

Prefer:

- Explicit code
- Small functions
- Reusable components
- Strong typing

Avoid:

- Premature abstractions
- Over-engineering
- Duplicate code

---

# Security

Never:

- Commit secrets
- Commit .env
- Hardcode credentials

Always use environment variables.

---

# Database

Use:

- Alembic migrations

Never:

- Modify production schemas manually.

---

# Deployment

Production environment:

Frontend

Render

Backend

Render

Database

Neon PostgreSQL

Deployment must be reproducible.

---

# Testing

Every significant business feature should include tests.

Prefer:

- Unit tests
- Integration tests

## Windows Node/NPM Tooling

On Windows, AI agents may run in a shell that does not inherit recently updated
user PATH values. If frontend checks cannot find Node or NPM, first use the
project-standard PowerShell prefix:

```powershell
$env:Path = 'C:\Program Files\nodejs;' + "$env:APPDATA\npm;" + $env:Path
```

Then invoke NPM as `npm.cmd`, not bare `npm`, because PowerShell may prefer
`npm.ps1` and block it under the local execution policy.

---

# Documentation

Documentation is mandatory.

Keep updated:

docs/

- architecture.md
- api.md
- database.md
- deployment.md
- roadmap.md
- backlog.md
- backlog_hist.md

Backlog maintenance:

- `docs/backlog.md` must contain only active or unresolved work, such as
  `IN_PROGRESS`, `PENDING_REVIEW`, `PLANNED`, `BLOCKED`, `DEFERRED`, and active
  review findings.
- `docs/backlog_hist.md` is the historical archive for completed work.
- When a ticket reaches `DONE`, move the full ticket entry from
  `docs/backlog.md` to `docs/backlog_hist.md` instead of leaving it in the
  active backlog.
- Keep `docs/project-status.md` synchronized with both files.

---

# Decision Making

When several solutions are possible:

1. Compare options.
2. Explain trade-offs.
3. Recommend one.
4. Justify the decision.

Never choose arbitrarily.

---

# Quality Standard

Every contribution should be production-ready.

Before considering a task complete, verify:

✓ Clean architecture

✓ No duplicated logic

✓ Proper validation

✓ Error handling

✓ Tests updated

✓ Documentation updated

✓ Environment variables documented

✓ Deployment unaffected

---

# Final Goal

The objective is not simply to generate code.

The objective is to collaboratively build a production-quality application that can evolve over time while remaining maintainable, secure and enjoyable to work on.
