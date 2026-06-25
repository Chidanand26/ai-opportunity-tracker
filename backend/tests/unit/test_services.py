"""Unit tests for catalog application services.

Repositories are mocked with AsyncMock so these tests are fast and need no
database. They assert the use-case logic each service adds on top of its
repositories: validation, duplicate detection, fingerprinting, and pagination.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.application.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.application.services.opportunity_service import OpportunityService
from app.application.services.organization_service import OrganizationService
from app.application.services.professor_service import ProfessorService
from app.application.services.source_service import SourceService
from app.domain.entities.opportunity import Opportunity
from app.domain.entities.organization import Organization
from app.domain.entities.professor import Professor
from app.domain.entities.source import Source
from app.domain.enums import OpportunityType, OrganizationType, SourceType

# ── Factories ─────────────────────────────────────────────────────────────────


def an_org(id: int | None = 1, name: str = "MIT") -> Organization:
    return Organization(id=id, name=name, org_type=OrganizationType.UNIVERSITY)


def a_source(id: int | None = 1, org_id: int | None = 1) -> Source:
    return Source(
        id=id,
        name="MIT Feed",
        url="https://mit.edu/feed.rss",
        source_type=SourceType.RSS_FEED,
        adapter_class="rss_feed",
        organization_id=org_id,
    )


def an_opportunity(id: int | None = None, fingerprint: str = "") -> Opportunity:
    return Opportunity(
        id=id,
        title="ML Internship",
        opportunity_type=OpportunityType.RESEARCH_INTERNSHIP,
        source_id=1,
        url="https://mit.edu/jobs/ml",
        fingerprint=fingerprint,
        organization_id=1,
    )


# ── OrganizationService ───────────────────────────────────────────────────────


class TestOrganizationService:
    async def test_get_returns_entity(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = an_org()
        service = OrganizationService(repo)
        result = await service.get(1)
        assert result.name == "MIT"

    async def test_get_missing_raises(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None
        service = OrganizationService(repo)
        with pytest.raises(EntityNotFoundError):
            await service.get(999)

    async def test_create_rejects_duplicate_name(self):
        repo = AsyncMock()
        repo.get_by_name.return_value = an_org()
        service = OrganizationService(repo)
        with pytest.raises(DuplicateEntityError):
            await service.create(an_org(id=None))

    async def test_create_persists_when_unique(self):
        repo = AsyncMock()
        repo.get_by_name.return_value = None
        repo.save.return_value = an_org()
        service = OrganizationService(repo)
        result = await service.create(an_org(id=None))
        assert result.id == 1
        repo.save.assert_awaited_once()

    async def test_get_or_create_returns_existing(self):
        repo = AsyncMock()
        repo.get_by_name.return_value = an_org()
        service = OrganizationService(repo)
        result = await service.get_or_create("MIT", OrganizationType.UNIVERSITY)
        assert result.id == 1
        repo.save.assert_not_called()

    async def test_get_or_create_creates_when_absent(self):
        repo = AsyncMock()
        repo.get_by_name.return_value = None
        repo.save.return_value = an_org(name="Stanford")
        service = OrganizationService(repo)
        result = await service.get_or_create("Stanford", OrganizationType.UNIVERSITY)
        assert result.name == "Stanford"
        repo.save.assert_awaited_once()

    async def test_update_missing_raises(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None
        service = OrganizationService(repo)
        with pytest.raises(EntityNotFoundError):
            await service.update(an_org())


# ── ProfessorService ──────────────────────────────────────────────────────────


class TestProfessorService:
    async def test_create_validates_organization_exists(self):
        professors = AsyncMock()
        organizations = AsyncMock()
        organizations.get_by_id.return_value = None
        service = ProfessorService(professors, organizations)
        with pytest.raises(ValidationError):
            await service.create(Professor(name="Dr. X", organization_id=42))
        professors.save.assert_not_called()

    async def test_create_persists_with_valid_org(self):
        professors = AsyncMock()
        organizations = AsyncMock()
        organizations.get_by_id.return_value = an_org()
        professors.save.return_value = Professor(id=5, name="Dr. X", organization_id=1)
        service = ProfessorService(professors, organizations)
        result = await service.create(Professor(name="Dr. X", organization_id=1))
        assert result.id == 5

    async def test_get_missing_raises(self):
        professors = AsyncMock()
        professors.get_by_id.return_value = None
        service = ProfessorService(professors, AsyncMock())
        with pytest.raises(EntityNotFoundError):
            await service.get(123)


# ── SourceService ─────────────────────────────────────────────────────────────


class TestSourceService:
    async def test_register_rejects_unknown_org(self):
        sources = AsyncMock()
        organizations = AsyncMock()
        organizations.get_by_id.return_value = None
        service = SourceService(sources, organizations)
        with pytest.raises(ValidationError):
            await service.register(a_source(id=None, org_id=77))
        sources.save.assert_not_called()

    async def test_register_allows_null_org(self):
        sources = AsyncMock()
        organizations = AsyncMock()
        sources.save.return_value = a_source(org_id=None)
        service = SourceService(sources, organizations)
        result = await service.register(a_source(id=None, org_id=None))
        assert result.id == 1
        organizations.get_by_id.assert_not_called()

    async def test_set_active_toggles_and_saves(self):
        sources = AsyncMock()
        sources.get_by_id.return_value = a_source()
        sources.update.side_effect = lambda s: s
        service = SourceService(sources, AsyncMock())
        result = await service.set_active(1, is_active=False)
        assert result.is_active is False


# ── OpportunityService ────────────────────────────────────────────────────────


class _OppContext:
    """Bundles an OpportunityService with its three mocked repositories."""

    def __init__(self) -> None:
        self.opportunities = AsyncMock()
        self.sources = AsyncMock()
        self.organizations = AsyncMock()
        self.service = OpportunityService(
            self.opportunities, self.sources, self.organizations
        )


class TestOpportunityService:
    async def test_create_rejects_unknown_source(self):
        ctx = _OppContext()
        ctx.sources.get_by_id.return_value = None
        with pytest.raises(ValidationError):
            await ctx.service.create(an_opportunity())
        ctx.opportunities.save.assert_not_called()

    async def test_create_generates_fingerprint(self):
        ctx = _OppContext()
        ctx.sources.get_by_id.return_value = a_source()
        ctx.organizations.get_by_id.return_value = an_org()
        ctx.opportunities.get_by_fingerprint.return_value = None
        ctx.opportunities.save.side_effect = lambda o: o
        result = await ctx.service.create(an_opportunity(fingerprint=""))
        assert result.fingerprint != ""
        assert len(result.fingerprint) == 16

    async def test_create_rejects_duplicate_fingerprint(self):
        ctx = _OppContext()
        ctx.sources.get_by_id.return_value = a_source()
        ctx.organizations.get_by_id.return_value = an_org()
        ctx.opportunities.get_by_fingerprint.return_value = an_opportunity(id=9, fingerprint="x")
        with pytest.raises(DuplicateEntityError):
            await ctx.service.create(an_opportunity(fingerprint="abc123def4567890"))

    async def test_list_builds_page_with_total(self):
        ctx = _OppContext()
        ctx.opportunities.list_active.return_value = [an_opportunity(id=1, fingerprint="a")]
        ctx.opportunities.count_active.return_value = 5
        page = await ctx.service.list_active(limit=1, offset=0)
        assert page.total == 5
        assert len(page.items) == 1
        assert page.has_more is True

    async def test_list_passes_filters_to_both_calls(self):
        ctx = _OppContext()
        ctx.opportunities.list_active.return_value = []
        ctx.opportunities.count_active.return_value = 0
        await ctx.service.list_active(
            opportunity_type=OpportunityType.FELLOWSHIP, organization_id=3
        )
        ctx.opportunities.list_active.assert_awaited_once()
        ctx.opportunities.count_active.assert_awaited_once_with(
            opportunity_type=OpportunityType.FELLOWSHIP, organization_id=3
        )

    async def test_deactivate_sets_inactive(self):
        ctx = _OppContext()
        ctx.opportunities.get_by_id.return_value = an_opportunity(id=1, fingerprint="a")
        ctx.opportunities.update.side_effect = lambda o: o
        result = await ctx.service.deactivate(1)
        assert result.is_active is False
