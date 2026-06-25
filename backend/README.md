# Backend

FastAPI application following clean architecture. Dependencies point inward: infrastructure
knows about domain; domain knows nothing about infrastructure.

## Layer Map

```
app/
├── core/          Cross-cutting: config (Pydantic Settings), structured logging
├── domain/        Pure Python — zero framework imports
│   ├── enums.py   All StrEnums: OpportunityType, SourceType, ScrapeStatus, ...
│   ├── entities/  Core data structures (dataclasses)
│   ├── ports/     Interfaces (Protocols): repos, LLM, notifier, scraper
│   └── value_objects/  Immutable typed wrappers (Fingerprint, Location, Money)
├── application/   Use cases — orchestration only, no infrastructure details
│   ├── services/  OpportunityService, MatchingService, DedupService, ...
│   └── dto/       Input/output data shapes for use cases
├── tools/         Agent-ready: thin callable wrappers over services (Tool protocol)
├── agents/        Future autonomous agents (scaffolded, not yet implemented)
├── infrastructure/  Adapters — implement domain/ports
│   ├── db/        SQLAlchemy models, session factory, repositories
│   ├── scrapers/  Playwright + BeautifulSoup source adapters
│   ├── llm/       OpenAI / Anthropic provider adapters
│   ├── notifications/  SMTP / SendGrid email adapters
│   └── cache/     Redis client helpers
├── api/           FastAPI routers and Pydantic request/response schemas
└── workers/       Celery app, beat schedule, task definitions
```

## Entity Relationship Diagram

```mermaid
erDiagram
    organizations {
        int id PK
        string name
        string org_type
        string website
        string country
        string city
        jsonb metadata
    }

    professors {
        int id PK
        int organization_id FK
        string name
        string email
        string department
        string lab_name
        jsonb research_areas
        bool is_accepting_students
    }

    sources {
        int id PK
        int organization_id FK
        string name
        string url
        string source_type
        string adapter_class
        bool is_active
        int scrape_frequency_hours
        jsonb config
        timestamp last_scraped_at
    }

    skills {
        int id PK
        string name
        string category
        jsonb aliases
    }

    opportunities {
        int id PK
        int source_id FK
        int organization_id FK
        int professor_id FK
        string title
        string opportunity_type
        text description
        text summary
        string url
        string fingerprint
        string location_type
        numeric stipend_amount
        date application_deadline
        bool is_active
        jsonb raw_data
    }

    opportunity_skills {
        int opportunity_id FK
        int skill_id FK
    }

    user_profiles {
        int id PK
        int user_id
        string display_name
        string email
        string degree_level
        int graduation_year
        jsonb preferred_opportunity_types
        jsonb preferred_locations
        bool notification_email_enabled
        string notification_frequency
        int min_match_score_for_email
    }

    profile_skills {
        int profile_id FK
        int skill_id FK
        string proficiency_level
    }

    opportunity_matches {
        int id PK
        int profile_id FK
        int opportunity_id FK
        int match_score
        text match_rationale
        bool is_saved
        bool is_applied
        timestamp applied_at
        bool is_notified
    }

    notifications {
        int id PK
        int profile_id FK
        int opportunity_match_id FK
        string notification_type
        string channel
        string subject
        text body
        timestamp sent_at
        bool is_read
    }

    scrape_jobs {
        int id PK
        int source_id FK
        string celery_task_id
        string status
        timestamp started_at
        timestamp completed_at
        int opportunities_found
        int opportunities_new
        text error_message
    }

    scrape_results {
        int id PK
        int scrape_job_id FK
        int opportunity_id FK
        string raw_url
        string fingerprint
        bool was_duplicate
        bool was_rejected
        string rejection_reason
    }

    organizations ||--o{ professors : "employs"
    organizations ||--o{ sources : "has"
    organizations ||--o{ opportunities : "posts"
    professors ||--o{ opportunities : "posts"
    sources ||--o{ opportunities : "yields"
    sources ||--o{ scrape_jobs : "triggers"
    scrape_jobs ||--o{ scrape_results : "produces"
    opportunities |o--o{ scrape_results : "created_from"
    opportunities }o--o{ skills : "requires (opportunity_skills)"
    user_profiles }o--o{ skills : "has (profile_skills)"
    user_profiles ||--o{ opportunity_matches : "has"
    opportunities ||--o{ opportunity_matches : "matched_to"
    user_profiles ||--o{ notifications : "receives"
    opportunity_matches |o--o{ notifications : "triggers"
```

## Key Design Decisions

| Decision | Reason |
|---|---|
| `fingerprint` unique constraint on `opportunities` | Deterministic dedup — same posting scraped twice creates zero duplicates |
| `raw_data JSONB` on `opportunities` | Never lose raw scrape payload; re-parse without re-scraping |
| `summary TEXT` on `opportunities` | AI-generated summary cached in DB; no repeat LLM calls |
| `user_id` on `user_profiles` | Single user now (always 1); multi-user is a FK + auth change, not a schema rewrite |
| `is_accepting_students` on `professors` | Feeds ProfessorSuggesterAgent; null = "not yet scraped" |
| `metadata JSONB` on several tables | Flexible per-source extra fields without schema churn |
| `ScrapeResult` per posting per job | Full audit trail: dedup rate, rejection rate, ingestion success per run |
| String columns for enum values | Avoids `ALTER TYPE` in PostgreSQL when adding new enum variants |

## Extension Points

- **New opportunity source**: add a class in `infrastructure/scrapers/sources/` implementing `SourceAdapter`, register in `infrastructure/scrapers/registry.py`.
- **New LLM provider**: add a class in `infrastructure/llm/` implementing `LLMPort`.
- **New notification channel**: add a class in `infrastructure/notifications/` implementing `NotifierPort`.
- **New agent**: add a class in `agents/` implementing `Agent`, expose via a Celery task.
- **Multi-user**: add a `users` table, remove `default_user_id=1`, wire auth middleware.

## Running

```bash
make up             # start all services
make migrate        # apply migrations
make seed           # seed default user + example sources
make test           # full test suite
make shell-api      # bash into API container
```
