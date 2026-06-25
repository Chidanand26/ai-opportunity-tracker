# Application Layer

Use-case orchestration. Services depend only on **domain ports** (Protocols),
never on concrete infrastructure — Dependency Inversion in practice. They add
validation, duplicate detection, fingerprinting, and pagination on top of the
repositories.

## Services

| Service | Responsibility | Repositories used |
|---|---|---|
| `OrganizationService` | CRUD + dedup `get_or_create` for institutions | organizations |
| `ProfessorService` | CRUD; validates parent organization exists | professors, organizations |
| `SourceService` | register/update/activate sources; list due-for-scrape | sources, organizations |
| `OpportunityService` | paginated listing, search, create (fingerprint + dedup), deactivate | opportunities, sources, organizations |

`MatchingService` and `NotificationService` are intentionally **not** here yet:
they depend on `LLMPort` (Phase 6) and `NotifierPort` (Phase 7) implementations.
They will be added when those adapters land, to avoid placeholder stubs.

## Error model (`app/application/exceptions.py`)

| Exception | Meaning | Maps to HTTP |
|---|---|---|
| `EntityNotFoundError` | Lookup found nothing | 404 |
| `DuplicateEntityError` | Uniqueness rule violated | 409 |
| `ValidationError` | Business rule failed pre-persistence | 422 |

The API layer translates these; services stay framework-free.

## DTOs

- `Page[T]` (`dto/pagination.py`) — items + total + limit + offset, with
  `has_more`. Returned by list endpoints so the frontend can paginate.

## Dependency injection

`app/core/dependencies.py` provides `get_*_service()` functions. Each composes a
service from the repository providers. Because `get_db` is request-scoped, all
repositories within one request share a single `AsyncSession`, so a service's
multi-repository use case runs in one transaction.

```python
from app.core.dependencies import get_opportunity_service
from app.application.services import OpportunityService

@router.get("/opportunities")
async def list_opportunities(
    service: Annotated[OpportunityService, Depends(get_opportunity_service)],
):
    return await service.list_active()
```

## Testing

- `tests/unit/test_services.py` — mocked repositories, no DB, fast.
- `tests/integration/test_services.py` — real repositories against PostgreSQL.
