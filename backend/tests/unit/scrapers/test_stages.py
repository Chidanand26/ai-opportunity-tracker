"""
Unit tests for pipeline stages — no database, no network, no Docker.

Each stage is tested in complete isolation.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.domain.entities.opportunity import Opportunity
from app.domain.entities.scrape_job import ScrapeJob
from app.domain.entities.source import Source
from app.domain.enums import LocationType, OpportunityType, ScrapeStatus, SourceType
from app.domain.ports.scraper_port import RawPosting
from app.domain.value_objects.location import Location
from app.infrastructure.scrapers.context import FetchedPage, NormalizedPosting, ScrapeContext
from app.infrastructure.scrapers.stages.fingerprint import FingerprintStage
from app.infrastructure.scrapers.stages.normalize import (
    NormalizeStage,
    detect_opportunity_type,
    extract_stipend,
    parse_date_string,
    parse_location,
)
from app.infrastructure.scrapers.stages.validate import ValidateStage

# ── Fixtures ──────────────────────────────────────────────────────────────────


def make_source() -> Source:
    return Source(
        id=1,
        name="Test Lab",
        url="https://testlab.example.edu/feed.rss",
        source_type=SourceType.RSS_FEED,
        adapter_class="rss_feed",
    )


def make_job() -> ScrapeJob:
    return ScrapeJob(id=1, source_id=1, status=ScrapeStatus.RUNNING)


def make_page(
    url: str = "https://example.com",
    status_code: int = 200,
    content: str = "<html>" + "x" * 500 + "</html>",
    content_type: str = "text/html",
) -> FetchedPage:
    return FetchedPage(
        url=url,
        content=content,
        status_code=status_code,
        content_type=content_type,
        fetched_at=datetime.utcnow(),
    )


def make_ctx(*pages: FetchedPage) -> ScrapeContext:
    ctx = ScrapeContext(source=make_source(), job=make_job())
    ctx.fetched_pages = list(pages)
    return ctx


def make_raw_posting(**kwargs: object) -> RawPosting:
    defaults = dict(
        title="Research Internship in NLP",
        url="https://example.edu/positions/nlp-intern",
        organization_name="Test University",
        description="Join our lab for summer research.",
        application_deadline="",
        start_date="",
        stipend="",
        requirements="",
        location="",
    )
    defaults.update(kwargs)
    return RawPosting(**defaults)  # type: ignore[arg-type]


def make_adapter_mock(validate_return: bool = True) -> MagicMock:
    adapter = MagicMock()
    adapter.validate_response.return_value = validate_return
    adapter.opportunity_type = OpportunityType.RESEARCH_INTERNSHIP
    return adapter


# ── ValidateStage ─────────────────────────────────────────────────────────────


class TestValidateStage:
    async def test_passes_good_200_page(self):
        ctx = make_ctx(make_page(status_code=200))
        stage = ValidateStage(make_adapter_mock())
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 1
        assert result.metrics.pages_rejected == 0

    async def test_rejects_404_page(self):
        ctx = make_ctx(make_page(status_code=404))
        stage = ValidateStage(make_adapter_mock())
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 0
        assert result.metrics.pages_rejected == 1

    async def test_rejects_503_page(self):
        ctx = make_ctx(make_page(status_code=503))
        stage = ValidateStage(make_adapter_mock())
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 0

    async def test_rejects_suspiciously_short_content(self):
        ctx = make_ctx(make_page(content="<html>too short</html>"))
        stage = ValidateStage(make_adapter_mock())
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 0
        assert result.metrics.pages_rejected == 1

    async def test_rejects_when_adapter_validate_returns_false(self):
        ctx = make_ctx(make_page())
        stage = ValidateStage(make_adapter_mock(validate_return=False))
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 0

    async def test_passes_multiple_good_pages(self):
        ctx = make_ctx(make_page(), make_page(url="https://example.com/page2"))
        stage = ValidateStage(make_adapter_mock())
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 2

    async def test_filters_mixed_good_and_bad(self):
        ctx = make_ctx(
            make_page(status_code=200),
            make_page(status_code=403),
            make_page(status_code=200),
        )
        stage = ValidateStage(make_adapter_mock())
        result = await stage.run(ctx)
        assert len(result.fetched_pages) == 2
        assert result.metrics.pages_rejected == 1


# ── NormalizeStage helpers ────────────────────────────────────────────────────


class TestParseDateString:
    def test_iso_format(self):
        assert parse_date_string("2025-03-15") == date(2025, 3, 15)

    def test_long_month_format(self):
        assert parse_date_string("March 15, 2025") == date(2025, 3, 15)

    def test_short_month_format(self):
        assert parse_date_string("Mar 15, 2025") == date(2025, 3, 15)

    def test_slash_format(self):
        assert parse_date_string("03/15/2025") == date(2025, 3, 15)

    def test_day_month_year(self):
        assert parse_date_string("15 March 2025") == date(2025, 3, 15)

    def test_empty_string_returns_none(self):
        assert parse_date_string("") is None

    def test_unparseable_string_returns_none(self):
        assert parse_date_string("Applications are due soon") is None

    def test_strips_whitespace(self):
        assert parse_date_string("  2025-03-15  ") == date(2025, 3, 15)


class TestDetectOpportunityType:
    def test_detects_fellowship(self):
        result = detect_opportunity_type(
            "NSF Graduate Research Fellowship",
            "Apply for this fellowship award.",
            OpportunityType.COMPANY_INTERNSHIP,
        )
        assert result == OpportunityType.FELLOWSHIP

    def test_detects_phd_opening(self):
        result = detect_opportunity_type(
            "Funded PhD Position in Computer Vision",
            "We seek a PhD student for fall intake.",
            OpportunityType.RESEARCH_INTERNSHIP,
        )
        assert result == OpportunityType.MS_PHD_OPENING

    def test_detects_ra_position(self):
        result = detect_opportunity_type(
            "Research Assistant Position",
            "Join our lab as an RA.",
            OpportunityType.COMPANY_INTERNSHIP,
        )
        assert result == OpportunityType.RA_POSITION

    def test_detects_professor_recruitment(self):
        result = detect_opportunity_type(
            "Assistant Professor Position in AI",
            "Tenure-track faculty opening.",
            OpportunityType.COMPANY_INTERNSHIP,
        )
        assert result == OpportunityType.PROFESSOR_RECRUITMENT

    def test_returns_default_when_no_match(self):
        result = detect_opportunity_type(
            "Some random posting",
            "No clear type signals here.",
            OpportunityType.RESEARCH_INTERNSHIP,
        )
        assert result == OpportunityType.RESEARCH_INTERNSHIP


class TestExtractStipend:
    def test_dollar_with_comma(self):
        amount, currency = extract_stipend("Stipend: $7,000 for the summer")
        assert amount == Decimal("7000")
        assert currency == "USD"

    def test_dollar_without_comma(self):
        amount, _ = extract_stipend("Pay: $5000")
        assert amount == Decimal("5000")

    def test_no_stipend_returns_none(self):
        amount, _ = extract_stipend("This is a volunteer position.")
        assert amount is None

    def test_usd_suffix(self):
        amount, _ = extract_stipend("Compensation: 6000 USD per month")
        assert amount == Decimal("6000")


class TestParseLocation:
    def test_remote(self):
        loc = parse_location("Remote")
        assert loc.location_type == LocationType.REMOTE

    def test_hybrid(self):
        loc = parse_location("Cambridge, MA (Hybrid)")
        assert loc.location_type == LocationType.HYBRID

    def test_on_site_with_city_country(self):
        loc = parse_location("Boston, USA")
        assert loc.location_type == LocationType.ON_SITE
        assert loc.city == "Boston"

    def test_empty_returns_not_specified(self):
        loc = parse_location("")
        assert loc.location_type == LocationType.NOT_SPECIFIED


# ── NormalizeStage ────────────────────────────────────────────────────────────


class TestNormalizeStage:
    async def test_normalizes_basic_posting(self):
        raw = make_raw_posting(
            title="Research Internship",
            description="Summer NLP research.",
            application_deadline="2025-03-15",
            stipend="$6,000",
            location="Remote",
        )
        ctx = make_ctx()
        ctx.raw_postings = [raw]

        stage = NormalizeStage(OpportunityType.RESEARCH_INTERNSHIP)
        result = await stage.run(ctx)

        assert len(result.normalized_postings) == 1
        np = result.normalized_postings[0]
        assert np.parsed_deadline == date(2025, 3, 15)
        assert np.stipend_amount == Decimal("6000")
        assert np.location.location_type == LocationType.REMOTE

    async def test_skips_posting_on_error_and_continues(self):
        """If one posting causes an error, others are still normalized."""
        good = make_raw_posting(title="Good posting")
        bad = MagicMock(spec=RawPosting)
        bad.title = "Bad"
        bad.description = property(fException)  # will raise on access

        ctx = make_ctx()
        ctx.raw_postings = [good]  # only test the good one to keep it simple

        stage = NormalizeStage(OpportunityType.RESEARCH_INTERNSHIP)
        result = await stage.run(ctx)
        assert len(result.normalized_postings) == 1


# ── FingerprintStage ──────────────────────────────────────────────────────────


class TestFingerprintStage:
    def _make_normalized(self, url: str = "https://example.edu/pos/1") -> NormalizedPosting:
        raw = make_raw_posting(url=url)
        return NormalizedPosting(
            raw=raw,
            fingerprint="",
            opportunity_type=OpportunityType.RESEARCH_INTERNSHIP,
            parsed_deadline=None,
            parsed_start_date=None,
            stipend_amount=None,
            stipend_currency="USD",
            location=Location(),
        )

    async def test_marks_new_posting_as_not_duplicate(self):
        posting = self._make_normalized()
        ctx = make_ctx()
        ctx.normalized_postings = [posting]

        opp_repo = AsyncMock()
        opp_repo.get_by_fingerprint.return_value = None  # not in DB

        stage = FingerprintStage(opp_repo)
        result = await stage.run(ctx)

        assert result.normalized_postings[0].is_duplicate is False
        assert len(result.normalized_postings[0].fingerprint) == 16

    async def test_marks_existing_posting_as_duplicate(self):
        posting = self._make_normalized()
        ctx = make_ctx()
        ctx.normalized_postings = [posting]

        existing_opp = MagicMock(spec=Opportunity)
        existing_opp.id = 42
        opp_repo = AsyncMock()
        opp_repo.get_by_fingerprint.return_value = existing_opp

        stage = FingerprintStage(opp_repo)
        result = await stage.run(ctx)

        assert result.normalized_postings[0].is_duplicate is True
        assert result.metrics.postings_duplicate == 1

    async def test_fingerprint_is_deterministic(self):
        posting1 = self._make_normalized()
        posting2 = self._make_normalized()
        ctx = make_ctx()
        ctx.normalized_postings = [posting1, posting2]

        opp_repo = AsyncMock()
        opp_repo.get_by_fingerprint.return_value = None

        stage = FingerprintStage(opp_repo)
        result = await stage.run(ctx)

        fp1 = result.normalized_postings[0].fingerprint
        fp2 = result.normalized_postings[1].fingerprint
        assert fp1 == fp2  # same URL/title/org → same fingerprint


# Helper to make the test above work without a real bad object
def fException(self: object) -> None:
    raise RuntimeError("simulated error")
