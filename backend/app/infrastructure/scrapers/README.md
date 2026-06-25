# Scrapers

Reusable scraping framework. Every source adapter inherits all infrastructure from
`BaseSourceAdapter` and implements only source-specific parsing logic (~30 lines).

## 7-Stage Pipeline Lifecycle

```
Source URL(s)
     │
     ▼
┌─────────────┐   robots.txt + rate limit + retry
│  FetchStage │──────────────────────────────────► FetchedPage list
└─────────────┘
     │
     ▼
┌──────────────┐  status code, content-type, min-length, adapter.validate_response()
│ValidateStage │──────────────────────────────────► filtered FetchedPage list
└──────────────┘
     │
     ▼
┌─────────────┐   adapter.parse_postings() — source-specific logic
│  ParseStage │──────────────────────────────────► RawPosting list
└─────────────┘
     │
     ▼
┌───────────────┐  dates, stipend, location, opportunity_type detection
│NormalizeStage │──────────────────────────────────► NormalizedPosting list
└───────────────┘
     │
     ▼
┌─────────────────┐  SHA-256 hash + repo lookup for duplicates
│FingerprintStage │──────────────────────────────────► NormalizedPosting list (marked)
└─────────────────┘
     │
     ▼
┌─────────────┐   save Opportunity + ScrapeResult per posting
│ PersistStage│──────────────────────────────────► Opportunity list
└─────────────┘
     │
     ▼
┌───────────┐   update ScrapeJob, log metrics, enqueue LLM enrichment
│ EmitStage │──────────────────────────────────► (side effects only)
└───────────┘
```

## Adding a New Adapter

1. Create `sources/<name>.py` inheriting from `BaseSourceAdapter`.
2. Set class-level config attributes (optional — all have sensible defaults).
3. Implement `get_start_urls()` and `parse_postings()` (required).
4. Register in `registry.py` under a short key.
5. Add sources to the DB with `adapter_class="<key>"`.

```python
# sources/my_lab.py
from bs4 import BeautifulSoup
from app.infrastructure.scrapers.adapter import BaseSourceAdapter
from app.domain.enums import OpportunityType
from app.domain.ports.scraper_port import RawPosting

class MyLabAdapter(BaseSourceAdapter):
    opportunity_type = OpportunityType.RA_POSITION
    requests_per_minute = 5

    async def get_start_urls(self, source):
        return [source.url]

    async def parse_postings(self, content, url, source):
        soup = BeautifulSoup(content, "lxml")
        postings = []
        for card in soup.select(".position-card"):
            postings.append(RawPosting(
                title=card.select_one("h3").get_text(strip=True),
                url=card.select_one("a")["href"],
                organization_name=source.name,
                description=card.select_one(".description").get_text(strip=True),
            ))
        return postings
```

## Key Files

| File | Purpose |
|---|---|
| `adapter.py` | `BaseSourceAdapter` — the base class all adapters inherit |
| `pipeline.py` | `ScrapePipeline` — chains stages, handles errors, marks ScrapeJob |
| `context.py` | `ScrapeContext`, `FetchedPage`, `NormalizedPosting` — pipeline state |
| `stages/` | 7 independent, testable stage classes |
| `http_client.py` | `HttpClient` — httpx wrapper with retry |
| `rate_limiter.py` | Per-domain async rate limiter |
| `robots.py` | robots.txt fetcher + cache |
| `browser.py` | `BrowserManager` — Playwright for JS-heavy pages |
| `registry.py` | Short-key → adapter class resolution |
| `sources/rss_feed.py` | Reference implementation (RSS 2.0 + Atom 1.0) |

## Configuration Reference

Adapter class attributes (set in subclass body):

| Attribute | Type | Default | Description |
|---|---|---|---|
| `opportunity_type` | `OpportunityType` | `RESEARCH_INTERNSHIP` | Default type assigned to postings |
| `needs_browser` | `bool` | `False` | Use Playwright instead of httpx |
| `requests_per_minute` | `int` | `10` | Per-domain rate limit |
| `respect_robots_txt` | `bool` | `True` | Check robots.txt before fetching |
| `timeout_seconds` | `int` | `30` | Request timeout |
| `user_agent` | `str` | `AIOpportunityTracker/1.0` | HTTP User-Agent header |
| `proxy` | `str \| None` | `None` | Proxy URL |

Source-level config overrides (in `source.config` JSONB):
- Any class attribute can be overridden per-source via `source.config`.
- Adapter-specific keys (e.g. `feed_type`, `title_filter`) are documented per adapter.

## Testing

```bash
# Run all scraper unit tests — no Docker, no network needed
docker compose exec api uv run pytest tests/unit/scrapers/ -v

# Test a specific adapter interactively
docker compose exec api python -c "
import asyncio
from app.domain.entities.source import Source
from app.domain.enums import SourceType
from app.infrastructure.scrapers.sources.rss_feed import RssFeedAdapter

async def main():
    source = Source(
        id=1, name='Test', url='https://feeds.feedburner.com/example',
        source_type=SourceType.RSS_FEED, adapter_class='rss_feed',
    )
    async with RssFeedAdapter() as adapter:
        print(await adapter.get_start_urls(source))

asyncio.run(main())
"
```
