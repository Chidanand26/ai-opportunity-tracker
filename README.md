# AI Opportunity Tracker

An AI-powered system that automatically finds and ranks internships, research positions,
fellowships, scholarships, and more — tailored to your profile.

## Quick Start

```bash
# 1. Copy and fill in your environment variables
cp .env.example .env

# 2. Start all services
make up

# 3. Run database migrations
make migrate

# 4. Seed the default user
make seed

# 5. Open the dashboard
open http://localhost:5173

# 6. Open the API docs
open http://localhost:8000/docs
```

## Architecture

```
backend/   FastAPI · Celery · PostgreSQL · Redis · Playwright · LLM
frontend/  React · Vite · Tailwind CSS · TanStack Query
infra/     Docker · deployment configs
```

See each subdirectory's README for detailed documentation.

## Development Commands

| Command | Description |
|---|---|
| `make up` | Start all Docker services |
| `make down` | Stop all services |
| `make logs` | Stream all logs |
| `make logs-api` | Stream API logs |
| `make migrate` | Apply pending migrations |
| `make migrate-create MSG="..."` | Create a new migration |
| `make test` | Run the full test suite |
| `make lint` | Run ruff linter |
| `make format` | Run ruff formatter |
| `make typecheck` | Run mypy |
| `make shell-api` | Shell into API container |
| `make shell-db` | psql into the database |
