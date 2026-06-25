# AI Opportunity Tracker

An AI-powered system that automatically finds, ranks, and notifies you of internships,
research positions, RA roles, fellowships, scholarships, and more — tailored to your profile.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Commands](#development-commands)
- [Architecture](#architecture)
- [Project Structure](#project-structure)

---

## Prerequisites

Install all tools below before running the project for the first time.

### 1. Docker Desktop *(required)*

Docker Desktop is the recommended container runtime on all platforms.
It bundles Docker Engine, Docker Compose, and a GUI for managing containers.

| Platform | Download & Install |
|---|---|
| **Windows** | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — enable the **WSL 2 backend** during setup |
| **macOS** | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) — Apple Silicon and Intel both supported |
| **Linux** | [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) — install Docker Engine + the Compose plugin |

After installation, verify Docker is running:

```bash
docker --version        # Docker version 26.x or newer
docker compose version  # Docker Compose version v2.x or newer
```

> **Windows note:** Docker Desktop requires Windows 10/11 with WSL 2 enabled.
> Run `wsl --install` in an elevated PowerShell if WSL is not yet installed.

---

### 2. Git *(required)*

| Platform | Install |
|---|---|
| **Windows** | [git-scm.com](https://git-scm.com/download/win) — Git for Windows includes **Git Bash**, which is used for `make` commands |
| **macOS** | Pre-installed, or `brew install git` |
| **Linux** | `sudo apt install git` / `sudo dnf install git` |

> **Windows users:** All `make` commands in this guide require **Git Bash**
> (not Command Prompt or PowerShell). Git Bash ships with Git for Windows.
> Every command also has a `docker compose` equivalent shown in the
> [Development Commands](#development-commands) table that works natively in
> PowerShell and CMD.

---

### 3. Python 3.12+ *(required for uv)*

| Platform | Install |
|---|---|
| **Windows** | [python.org/downloads](https://www.python.org/downloads/) or `winget install Python.Python.3.12` |
| **macOS** | `brew install python@3.12` |
| **Linux** | `sudo apt install python3.12 python3.12-venv` |

Verify: `python --version` (Windows) or `python3 --version` (macOS/Linux).

---

### 4. uv — Python package manager *(required)*

`uv` manages the backend's virtual environment and dependencies.
It is 10–100× faster than pip and pip-tools.

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify: `uv --version`

> `uv` does **not** need to be installed on the host machine if you only use Docker
> for development — it is installed inside the container automatically. You only
> need it locally if you want to run Python tools outside Docker.

---

### 5. Node.js 20 LTS *(required for frontend)*

| Platform | Install |
|---|---|
| **Windows** | [nodejs.org](https://nodejs.org/) (LTS) or `winget install OpenJS.NodeJS.LTS` |
| **macOS** | `brew install node@20` |
| **Linux** | [nodesource.com](https://github.com/nodesource/distributions) or `nvm install 20` |

Verify: `node --version` (must be v20.x or higher).

> The frontend runs inside Docker for development. You only need Node.js locally
> to run `npm` commands outside the container (e.g. IDE type-checking).

---

### 6. make *(optional — Git Bash / Linux / macOS only)*

`make` provides short command aliases. Every `make` command has an equivalent
`docker compose` command — you do not need `make` to develop on Windows.

| Platform | Install |
|---|---|
| **Windows** | Included in Git Bash. Or: `choco install make` / `winget install GnuWin32.Make` |
| **macOS** | Pre-installed (part of Xcode CLI tools) |
| **Linux** | `sudo apt install make` |

---

## Quick Start

### Step 1 — Clone the repository

**Git Bash / macOS / Linux:**
```bash
git clone https://github.com/your-username/ai-opportunity-tracker.git
cd ai-opportunity-tracker
```

**PowerShell / CMD:**
```powershell
git clone https://github.com/your-username/ai-opportunity-tracker.git
cd ai-opportunity-tracker
```

---

### Step 2 — Create your `.env` file

**Git Bash / macOS / Linux:**
```bash
cp .env.example .env
```

**PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Command Prompt:**
```cmd
copy .env.example .env
```

Open `.env` in any editor and fill in the required values:

```env
SECRET_KEY=<generate a random string — see below>
ANTHROPIC_API_KEY=<your key from console.anthropic.com>
```

**Generate a secret key:**

All platforms (Python required):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> Windows users: use `python` not `python3` unless you have aliased it.

---

### Step 3 — Start all services

**Git Bash / macOS / Linux:**
```bash
make up
```

**PowerShell / CMD:**
```powershell
docker compose up -d
```

First run pulls images and builds containers — this takes 2–5 minutes.
Subsequent starts are instant.

---

### Step 4 — Apply database migrations

**Git Bash / macOS / Linux:**
```bash
make migrate
```

**PowerShell / CMD:**
```powershell
docker compose exec api uv run alembic upgrade head
```

---

### Step 5 — Seed the default user

**Git Bash / macOS / Linux:**
```bash
make seed
```

**PowerShell / CMD:**
```powershell
docker compose exec api uv run python scripts/seed.py
```

---

### Step 6 — Open the app

| URL | What it is |
|---|---|
| `http://localhost:5173` | React dashboard |
| `http://localhost:8000/docs` | FastAPI interactive docs (Swagger UI) |
| `http://localhost:8000/health/` | Liveness check |
| `http://localhost:8000/health/ready` | Readiness check (DB + Redis) |

**Open in browser:**

| Platform | Command |
|---|---|
| **macOS** | `open http://localhost:5173` |
| **Linux** | `xdg-open http://localhost:5173` |
| **Windows PowerShell** | `Start-Process http://localhost:5173` |
| **Windows CMD** | `start http://localhost:5173` |

---

## Development Commands

Every command is shown for all platforms.
All `docker compose` commands work identically on Windows, macOS, and Linux.

### Services

| Action | Git Bash / macOS / Linux | PowerShell / CMD |
|---|---|---|
| Start all services | `make up` | `docker compose up -d` |
| Stop all services | `make down` | `docker compose down` |
| Rebuild images | `make build` | `docker compose build` |
| Stream all logs | `make logs` | `docker compose logs -f` |
| Stream API logs | `make logs-api` | `docker compose logs -f api` |
| Stream worker logs | `make logs-worker` | `docker compose logs -f worker` |
| Shell into API container | `make shell-api` | `docker compose exec api bash` |
| psql into database | `make shell-db` | `docker compose exec db psql -U tracker tracker_db` |

---

### Database

| Action | Git Bash / macOS / Linux | PowerShell / CMD |
|---|---|---|
| Apply all migrations | `make migrate` | `docker compose exec api uv run alembic upgrade head` |
| Roll back one migration | `make migrate-down` | `docker compose exec api uv run alembic downgrade -1` |
| Create new migration | `make migrate-create MSG="add users"` | `docker compose exec api uv run alembic revision --autogenerate -m "add users"` |
| Seed default data | `make seed` | `docker compose exec api uv run python scripts/seed.py` |

---

### Testing & Code Quality

| Action | Git Bash / macOS / Linux | PowerShell / CMD |
|---|---|---|
| Run all tests | `make test` | `docker compose exec api uv run pytest tests/ -v --cov=app` |
| Run unit tests only | `make test-unit` | `docker compose exec api uv run pytest tests/unit/ -v` |
| Run integration tests | `make test-integration` | `docker compose exec api uv run pytest tests/integration/ -v` |
| Lint (ruff) | `make lint` | `docker compose exec api uv run ruff check app/ tests/` |
| Format code | `make format` | `docker compose exec api uv run ruff format app/ tests/` |
| Type check (mypy) | `make typecheck` | `docker compose exec api uv run mypy app/` |

---

### Scrapers

| Action | Git Bash / macOS / Linux | PowerShell / CMD |
|---|---|---|
| Install Playwright browsers | `make playwright-install` | `docker compose exec api uv run playwright install --with-deps chromium` |

---

## Architecture

```
backend/   Python 3.12 · FastAPI · Celery · PostgreSQL · Redis · Playwright · LLM
frontend/  React 18 · Vite 6 · Tailwind CSS 3 · TanStack Query v5
infra/     Docker · cloud deployment configs
```

**Layer diagram:**
```
Interface:   FastAPI routes · Celery tasks
Agents:      Future autonomous agents (scaffolded)
Application: Use cases / services
Tools:       Thin wrappers (callable by agents and services)
Domain:      Entities · value objects · ports — pure Python, zero framework deps
Infra:       PostgreSQL · Redis · Scrapers · LLM · Email
```

See [`backend/README.md`](backend/README.md) for the full architecture and ER diagram.

---

## Project Structure

```
ai-opportunity-tracker/
├── .env.example          ← copy to .env and fill in secrets
├── docker-compose.yml    ← all 6 services (db, redis, api, worker, beat, frontend)
├── Makefile              ← dev shortcuts (Git Bash / macOS / Linux)
├── backend/
│   ├── app/
│   │   ├── core/         ← config, logging
│   │   ├── domain/       ← entities, ports, value objects (pure Python)
│   │   ├── application/  ← services / use cases
│   │   ├── tools/        ← agent-callable tool wrappers
│   │   ├── agents/       ← future autonomous agents (scaffolded)
│   │   ├── infrastructure/  ← DB, scrapers, LLM, cache, notifications
│   │   ├── api/          ← FastAPI routers + Pydantic schemas
│   │   └── workers/      ← Celery app + tasks
│   ├── alembic/          ← database migrations
│   ├── tests/
│   │   ├── unit/         ← no infra needed (fast)
│   │   └── integration/  ← requires DB + Redis
│   └── pyproject.toml    ← Python deps + tooling config
├── frontend/
│   ├── src/
│   │   ├── api/          ← typed API client
│   │   ├── components/   ← reusable UI components
│   │   ├── features/     ← opportunity list, profile, admin
│   │   └── pages/        ← route-level pages
│   └── package.json
└── infra/
    └── README.md         ← cloud deployment notes (VPS / ECS / Cloud Run)
```

---

## Troubleshooting

### "docker compose" not found
Upgrade to Docker Desktop 4.x or install the Compose plugin separately.
Old Docker installations used `docker-compose` (with a hyphen); modern ones use `docker compose` (space).

### Port conflicts
If ports 5432, 6379, 8000, or 5173 are already in use, stop the conflicting process
or change the port mappings in `docker-compose.yml`.

### make: command not found (Windows)
Use the equivalent `docker compose` command from the table above.
Alternatively, install Git for Windows (which includes Git Bash with `make`).

### WSL 2 required (Windows)
Docker Desktop on Windows requires WSL 2. Run `wsl --install` in an elevated
PowerShell, restart, then start Docker Desktop again.

### Slow first build
The first `docker compose up --build` downloads base images (~2 GB total)
and installs Python/Node dependencies. Subsequent builds use the Docker layer
cache and are much faster.

### Database migration errors
If Alembic reports "Target database is not up to date", run:
```powershell
docker compose exec api uv run alembic stamp head
docker compose exec api uv run alembic upgrade head
```
