# Infrastructure

Deployment configuration. Application code is cloud-agnostic (twelve-factor);
only this directory changes when moving from Docker-local to a cloud provider.

## Local Development

Everything runs via `docker compose` from the project root. See the main README.

## Cloud Deployment (future)

The app is ready for cloud deployment without code changes because:

- All config comes from environment variables (Pydantic Settings)
- Services are stateless (API, worker, beat) — scale horizontally
- State lives only in PostgreSQL and Redis — use managed services (RDS, ElastiCache)
- Health checks are built in at `/health/` and `/health/ready`

### Deployment targets

| Target | Notes |
|---|---|
| VPS (Ubuntu + Docker) | Run `docker compose -f docker-compose.prod.yml up -d` |
| AWS ECS | Replace docker-compose with task definitions; use RDS + ElastiCache |
| GCP Cloud Run | Stateless services only (api); workers need Cloud Run Jobs or GKE |
| Fly.io | `fly deploy` — add fly.toml per service |

## Adding a Production Compose

Create `docker-compose.prod.yml` with:
- No volume mounts (use built images)
- No `--reload` flags
- Secrets from environment (not `.env` file)
- Resource limits per service
