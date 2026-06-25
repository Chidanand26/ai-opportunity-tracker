# ─────────────────────────────────────────────────────────────────────────────
# Makefile — development shortcuts
#
# Requires: make (included in Git Bash on Windows, pre-installed on macOS/Linux)
#
# Windows users have two options:
#   1. Git Bash (recommended) — run these make commands as-is
#   2. PowerShell / CMD      — use the docker compose equivalents shown in README.md
#
# Every target below is a thin wrapper over a `docker compose exec ...` command.
# If make is unavailable, run the docker compose command directly.
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help up down build logs test lint format typecheck migrate seed

# Default target
help:
	@echo "AI Opportunity Tracker — available commands"
	@echo ""
	@echo "  Requires: Git Bash (Windows), or any shell on macOS/Linux."
	@echo "  PowerShell/CMD users: see README.md for docker compose equivalents."
	@echo ""
	@echo "  Services"
	@echo "    make up                         Start all services (detached)"
	@echo "    make down                       Stop all services"
	@echo "    make build                      Rebuild Docker images"
	@echo "    make logs                       Stream logs (all services)"
	@echo "    make logs-api                   Stream API logs"
	@echo "    make logs-worker                Stream worker logs"
	@echo "    make shell-api                  bash shell in API container"
	@echo "    make shell-db                   psql in database container"
	@echo ""
	@echo "  Database"
	@echo "    make migrate                    Apply all pending migrations"
	@echo "    make migrate-create MSG='...'   Create a new migration"
	@echo "    make migrate-down               Roll back one migration"
	@echo "    make seed                       Seed default data"
	@echo ""
	@echo "  Quality"
	@echo "    make test                       Full test suite (with coverage)"
	@echo "    make test-unit                  Unit tests only (no infra)"
	@echo "    make test-integration           Integration tests"
	@echo "    make lint                       Ruff linter"
	@echo "    make format                     Ruff formatter"
	@echo "    make typecheck                  mypy type checker"
	@echo ""
	@echo "  Scrapers"
	@echo "    make playwright-install         Install Chromium in the container"

# ─── Services ───────────────────────────────────────────────────────────────

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

logs-%:
	docker compose logs -f $*

shell-api:
	docker compose exec api bash

shell-db:
	docker compose exec db psql -U $${POSTGRES_USER:-tracker} $${POSTGRES_DB:-tracker_db}

# ─── Database ────────────────────────────────────────────────────────────────

migrate:
	docker compose exec api uv run alembic upgrade head

migrate-create:
	@test -n "$(MSG)" || (echo "Usage: make migrate-create MSG='your description'" && exit 1)
	docker compose exec api uv run alembic revision --autogenerate -m "$(MSG)"

migrate-down:
	docker compose exec api uv run alembic downgrade -1

seed:
	docker compose exec api uv run python scripts/seed.py

# ─── Quality ─────────────────────────────────────────────────────────────────

test:
	docker compose exec api uv run pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:
	docker compose exec api uv run pytest tests/unit/ -v

test-integration:
	docker compose exec api uv run pytest tests/integration/ -v

lint:
	docker compose exec api uv run ruff check app/ tests/

format:
	docker compose exec api uv run ruff format app/ tests/

typecheck:
	docker compose exec api uv run mypy app/

# ─── Utilities ───────────────────────────────────────────────────────────────

# Install Playwright browsers inside the container
playwright-install:
	docker compose exec api uv run playwright install --with-deps chromium
