"""
NormalizeStage — converts RawPosting → NormalizedPosting.

Responsibilities:
  - Parse date strings into date objects (8 format attempts).
  - Detect opportunity type from title/description keywords.
  - Extract stipend amount from unstructured text.
  - Structure location into a Location value object.

Intentionally tolerant: if a field can't be parsed, it defaults to None/unknown
rather than rejecting the posting. The raw text is always preserved in raw_data.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.core.logging import get_logger
from app.domain.enums import LocationType, OpportunityType
from app.domain.ports.scraper_port import RawPosting
from app.domain.value_objects.location import Location
from app.infrastructure.scrapers.context import NormalizedPosting, ScrapeContext

logger = get_logger(__name__)

# ── Date parsing ──────────────────────────────────────────────────────────────

_DATE_FORMATS = [
    "%Y-%m-%d",           # 2025-03-15
    "%B %d, %Y",          # March 15, 2025
    "%b %d, %Y",          # Mar 15, 2025
    "%B %d %Y",           # March 15 2025
    "%m/%d/%Y",           # 03/15/2025
    "%d/%m/%Y",           # 15/03/2025
    "%d %B %Y",           # 15 March 2025
    "%d %b %Y",           # 15 Mar 2025
]


def parse_date_string(s: str) -> date | None:
    """Try each format in order; return the first that succeeds."""
    if not s:
        return None
    s = s.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


# ── Opportunity type detection ────────────────────────────────────────────────

# Order matters — more specific patterns first
_TYPE_KEYWORDS: list[tuple[OpportunityType, list[str]]] = [
    (OpportunityType.PROFESSOR_RECRUITMENT, [
        "faculty position", "assistant professor", "associate professor",
        "tenure-track", "hiring faculty", "open rank faculty",
    ]),
    (OpportunityType.MS_PHD_OPENING, [
        "phd position", "ph.d. position", "doctoral position", "phd opening",
        "ms/phd", "graduate student position", "funded phd",
    ]),
    (OpportunityType.FELLOWSHIP, [
        "fellowship", "postdoctoral fellow", "fellow program",
    ]),
    (OpportunityType.SCHOLARSHIP, [
        "scholarship", "financial award", "grant award",
    ]),
    (OpportunityType.RA_POSITION, [
        "research assistant", "ra position", "research associate",
        "graduate research assistant",
    ]),
    (OpportunityType.SUMMER_INTERNSHIP, [
        "summer intern", "summer program", "summer research",
        "summer undergraduate", "reu", "research experience for undergrad",
    ]),
    (OpportunityType.RESEARCH_INTERNSHIP, [
        "research intern", "research internship",
    ]),
    (OpportunityType.COMPANY_INTERNSHIP, [
        "software intern", "engineering intern", "product intern",
        "data science intern", "ml intern",
    ]),
]


def detect_opportunity_type(
    title: str,
    description: str,
    default: OpportunityType,
) -> OpportunityType:
    """Keyword scan of title + description; returns default if nothing matches."""
    text = (title + " " + description).lower()
    for opp_type, keywords in _TYPE_KEYWORDS:
        if any(kw in text for kw in keywords):
            return opp_type
    return default


# ── Stipend extraction ────────────────────────────────────────────────────────

_STIPEND_RE = re.compile(
    r"""
    \$\s*[\d,]+(?:\.\d{1,2})?          # $7,000 or $7000.00
    |
    \b[\d,]+(?:\.\d{1,2})?\s*          # 7000 USD / 7,000 per month
    (?:USD|usd|dollars?|per\s+month|\/month|per\s+week)
    """,
    re.VERBOSE | re.IGNORECASE,
)


def extract_stipend(text: str) -> tuple[Decimal | None, str]:
    """Return (amount, currency) or (None, 'USD') if no stipend found."""
    match = _STIPEND_RE.search(text)
    if not match:
        return None, "USD"
    raw = re.sub(r"[^\d.]", "", match.group())
    try:
        return Decimal(raw), "USD"
    except InvalidOperation:
        return None, "USD"


# ── Location parsing ──────────────────────────────────────────────────────────

_REMOTE_RE = re.compile(r"\bremote\b|\bvirtual\b|\bonline\b", re.IGNORECASE)
_HYBRID_RE = re.compile(r"\bhybrid\b|\bflexible\b", re.IGNORECASE)


def parse_location(raw_location: str) -> Location:
    """Convert a free-text location string to a typed Location value object."""
    if not raw_location:
        return Location()
    if _REMOTE_RE.search(raw_location):
        return Location(location_type=LocationType.REMOTE)
    if _HYBRID_RE.search(raw_location):
        # Best-effort: split "City, Country (Hybrid)" into parts
        parts = [p.strip() for p in re.split(r"[,/]", raw_location) if p.strip()]
        city = parts[0] if parts else ""
        country = parts[1] if len(parts) > 1 else ""
        return Location(location_type=LocationType.HYBRID, city=city, country=country)
    # On-site — try to extract city/country
    parts = [p.strip() for p in re.split(r"[,/]", raw_location) if p.strip()]
    city = parts[0] if parts else ""
    country = parts[-1] if len(parts) > 1 else ""
    return Location(location_type=LocationType.ON_SITE, city=city, country=country)


# ── Stage ─────────────────────────────────────────────────────────────────────


class NormalizeStage:
    """
    Convert each RawPosting into a NormalizedPosting.

    Failures per-posting are logged and the posting is marked rejected
    rather than crashing the whole stage.
    """

    def __init__(self, default_opportunity_type: OpportunityType) -> None:
        self._default_type = default_opportunity_type

    async def run(self, ctx: ScrapeContext) -> ScrapeContext:
        for raw in ctx.raw_postings:
            try:
                normalized = self._normalize(raw)
                ctx.normalized_postings.append(normalized)
            except Exception as exc:
                logger.warning(
                    "normalize_failed",
                    url=raw.url,
                    title=raw.title,
                    error=str(exc),
                )
                ctx.metrics.postings_rejected += 1
                ctx.errors.append(exc)

        logger.info(
            "normalize_stage_complete",
            input=len(ctx.raw_postings),
            output=len(ctx.normalized_postings),
            rejected=ctx.metrics.postings_rejected,
        )
        return ctx

    def _normalize(self, raw: RawPosting) -> NormalizedPosting:
        text = raw.description + " " + raw.stipend
        return NormalizedPosting(
            raw=raw,
            fingerprint="",  # filled by FingerprintStage
            opportunity_type=detect_opportunity_type(
                raw.title, raw.description, self._default_type
            ),
            parsed_deadline=parse_date_string(raw.application_deadline),
            parsed_start_date=parse_date_string(raw.start_date),
            stipend_amount=extract_stipend(text)[0],
            stipend_currency=extract_stipend(text)[1],
            location=parse_location(raw.location),
        )
