.PHONY: help up down build logs test lint format typecheck migrate seed

# Default target
help:
	@echo "AI Opportunity Tracker — available commands:"
	@echo ""
	@echo "  make up           Start all services (detached)"
	@echo "  make down         Stop all services"
	@echo "  make build        Rebuild Docker images"
	@echo "  make logs         Stream logs for all services"
	@echo "  make logs-api     Stream API logs only"
	@echo "  make shell-api    Open a shell in the API container"
	@echo "  make shell-db     Open psql in the DB container"
	@echo ""
	@echo "  make migrate      Apply all pending migrations"
	@echo "  make migrate-create MSG='description'  Create a new migration"
	@echo "  make seed         Seed the database with initial data"
	@echo ""
	@echo "  make test         Run the full test suite"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Run ruff formatter"
	@echo "  make typecheck    Run mypy type checker"

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
