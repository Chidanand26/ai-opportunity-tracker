# Backend

FastAPI application following clean architecture. Dependencies point inward: infrastructure
knows about domain; domain knows nothing about infrastructure.

## Layer Map

```
app/
├── core/          Cross-cutting: config (Pydantic Settings), structured logging
├── domain/        Pure Python business logic — zero framework imports
│   ├── entities/  Core data structures (Opportunity, Profile, Source, MatchScore)
│   ├── ports/     Interfaces (protocols) for repos, LLM, notifier, scraper
│   └── value_objects/  Immutable typed wrappers (Fingerprint, DateRange, Location)
├── application/   Use cases — orchestration only, no infrastructure details
│   ├── services/  OpportunityService, MatchingService, DedupService, ...
│   └── dto/       Input/output data shapes for use cases
├── tools/         Agent-ready: thin callable wrappers over services (Tool protocol)
├── agents/        Future autonomous agents (scaffolded, not yet implemented)
├── infrastructure/  Adapters — implement domain/ports
│   ├── db/        SQLAlchemy models, session, repositories
│   ├── scrapers/  Playwright + BeautifulSoup source adapters
│   ├── llm/       OpenAI / Anthropic provider adapters
│   ├── notifications/  SMTP / SendGrid email adapters
│   └── cache/     Redis helpers
├── api/           FastAPI routers and Pydantic request/response schemas
└── workers/       Celery app, beat schedule, task definitions
```

## Extension Points

- **New opportunity source**: add a class in `infrastructure/scrapers/sources/` implementing `SourceAdapter`, register in `infrastructure/scrapers/registry.py`.
- **New LLM provider**: add a class in `infrastructure/llm/` implementing the `LLMPort` protocol.
- **New notification channel**: add a class in `infrastructure/notifications/` implementing `NotifierPort`.
- **New agent**: add a class in `agents/` implementing `Agent`, expose via a Celery task.

## Testing

```bash
make test           # full suite with coverage
make test-unit      # domain + application (no infra dependencies)
make test-integration  # adapters (requires running db + redis)
```
