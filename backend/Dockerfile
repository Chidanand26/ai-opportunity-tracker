FROM python:3.12-slim

WORKDIR /app

# System dependencies — curl for healthchecks; rest for Playwright/lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv — the modern Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifest first (layer cache: only re-install when deps change)
COPY pyproject.toml ./

# Install all dependencies into the project venv
RUN uv sync --no-dev

# Copy application source
COPY . .

EXPOSE 8000

# Default command — overridden per-service in docker-compose.yml
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
