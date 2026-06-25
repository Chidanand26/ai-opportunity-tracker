FROM python:3.12-slim

WORKDIR /app

# ── System dependencies ───────────────────────────────────────────────────────
# curl  : used by health-check scripts and diagnostic tools
# libxml2-dev, libxslt1-dev : required by lxml (HTML/XML parser for scrapers)
# This layer is cached as long as the base image and package list are unchanged.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# ── uv ───────────────────────────────────────────────────────────────────────
# Copy the uv binary from the official image rather than downloading at build
# time — faster and works in air-gapped environments.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ── Dependency layer (cached until pyproject.toml or uv.lock changes) ─────────
# Copy ONLY the files that define the dependency set.
# Copying them before the source tree means Docker re-uses this layer on every
# build where only application code changed — not the dependencies.
COPY pyproject.toml uv.lock ./

# --frozen   : read the lockfile exactly; fail if it is out of sync with
#              pyproject.toml — guarantees reproducible installs in CI/Docker.
# --no-dev   : exclude development dependencies (pytest, mypy, ruff, etc.)
# --no-cache : avoids writing a uv HTTP cache inside the image layer
RUN uv sync --frozen --no-dev --no-cache

# ── Application source ────────────────────────────────────────────────────────
# Copied last so that code changes do not invalidate the dependency layer above.
# The .dockerignore file (backend/.dockerignore) excludes .venv, __pycache__,
# .pytest_cache, .env, logs, and other local artifacts before they reach here.
COPY . .

EXPOSE 8000

# Default command — overridden per-service in docker-compose.yml
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
