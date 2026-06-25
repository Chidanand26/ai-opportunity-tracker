"""Integration tests for catalog services against PostgreSQL.

These exercise each service through its real SQLAlchemy repositories, verifying
the use-case logic end-to-end against the database. They reuse the session
fixture from conftest.py (one connection, rolled back per test).
"""

from __future__ import annotations

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
from app.infrastructure.db.repositories.opportunity_repository import (
    SqlAlchemyOpportunityRepository,
)
from app.infrastructure.db.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.db.repositories.professor_repository import (
    SqlAlchemyProfessorRepository,
)
from app.infrastructure.db.repositories.source_repository import SqlAlchemySourceRepository

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ── Builders ──────────────────────────────────────────────────────────────────


def org_service(session) -> OrganizationService:
    return OrganizationService(SqlAlchemyOrganizationRepository(session))


def prof_service(session) -> ProfessorService:
    return ProfessorService(
        SqlAlchemyProfessorRepository(session),
        SqlAlchemyOrganizationRepository(session),
    )


def source_service(session) -> SourceService:
    return SourceService(
        SqlAlchemySourceRepository(session),
        SqlAlchemyOrganizationRepository(session),
    )


def opportunity_service(session) -> OpportunityService:
    return OpportunityService(
        SqlAlchemyOpportunityRepository(session),
        SqlAlchemySourceRepository(session),
        SqlAlchemyOrganizationRepository(session),
    )


async def seed_org(session, name: str = "Test University") -> Organization:
    return await org_service(session).create(
        Organization(name=name, org_type=OrganizationType.UNIVERSITY)
    )


async def seed_source(session, org_id: int) -> Source:
    return await source_service(session).register(
        Source(
            name="Test Feed",
            url="https://example.edu/feed.rss",
            source_type=SourceType.RSS_FEED,
            adapter_class="rss_feed",
            organization_id=org_id,
        )
    )


# ── OrganizationService ───────────────────────────────────────────────────────


class TestOrganizationServiceIntegration:
    async def test_create_and_get(self, session):
        service = org_service(session)
        created = await service.create(
            Organization(name="MIT", org_type=OrganizationType.UNIVERSITY)
        )
        fetched = await service.get(created.id)
        assert fetched.name == "MIT"

    async def test_create_duplicate_raises(self, session):
        service = org_service(session)
        await service.create(Organization(name="Dup U", org_type=OrganizationType.UNIVERSITY))
        with pytest.raises(DuplicateEntityError):
            await service.create(
                Organization(name="Dup U", org_type=OrganizationType.UNIVERSITY)
            )

    async def test_get_or_create_is_idempotent(self, session):
        service = org_service(session)
        a = await service.get_or_create("Idem U", OrganizationType.UNIVERSITY)
        b = await service.get_or_create("Idem U", OrganizationType.UNIVERSITY)
        assert a.id == b.id


# ── ProfessorService ──────────────────────────────────────────────────────────


class TestProfessorServiceIntegration:
    async def test_create_under_org(self, session):
        org = await seed_org(session)
        service = prof_service(session)
        prof = await service.create(
            Professor(name="Dr. Ada", organization_id=org.id, is_accepting_students=True)
        )
        assert prof.id is not None

    async def test_create_with_bad_org_raises(self, session):
        service = prof_service(session)
        with pytest.raises(ValidationError):
            await service.create(Professor(name="Dr. Nobody", organization_id=99999))

    async def test_list_accepting_students(self, session):
        org = await seed_org(session)
        service = prof_service(session)
        await service.create(
            Professor(name="Open Prof", organization_id=org.id, is_accepting_students=True)
        )
        await service.create(
            Professor(name="Closed Prof", organization_id=org.id, is_accepting_students=False)
        )
        accepting = await service.list_accepting_students()
        assert all(p.is_accepting_students for p in accepting)
        assert any(p.name == "Open Prof" for p in accepting)


# ── SourceService ─────────────────────────────────────────────────────────────


class TestSourceServiceIntegration:
    async def test_register_and_toggle(self, session):
        org = await seed_org(session)
        service = source_service(session)
        source = await service.register(
            Source(
                name="Lab Feed",
                url="https://lab.edu/feed.rss",
                source_type=SourceType.RSS_FEED,
                adapter_class="rss_feed",
                organization_id=org.id,
            )
        )
        assert source.is_active is True
        toggled = await service.set_active(source.id, is_active=False)
        assert toggled.is_active is False

    async def test_register_bad_org_raises(self, session):
        service = source_service(session)
        with pytest.raises(ValidationError):
            await service.register(
                Source(
                    name="Orphan Feed",
                    url="https://orphan.edu/feed.rss",
                    source_type=SourceType.RSS_FEED,
                    adapter_class="rss_feed",
                    organization_id=88888,
                )
            )


# ── OpportunityService ────────────────────────────────────────────────────────


class TestOpportunityServiceIntegration:
    async def _setup(self, session) -> Source:
        org = await seed_org(session)
        return await seed_source(session, org.id)

    async def test_create_generates_fingerprint_and_persists(self, session):
        source = await self._setup(session)
        service = opportunity_service(session)
        opp = await service.create(
            Opportunity(
                title="Summer ML Internship",
                opportunity_type=OpportunityType.SUMMER_INTERNSHIP,
                source_id=source.id,
                url="https://example.edu/jobs/ml",
                fingerprint="",
                organization_id=source.organization_id,
            )
        )
        assert opp.id is not None
        assert len(opp.fingerprint) == 16

    async def test_create_duplicate_fingerprint_raises(self, session):
        source = await self._setup(session)
        service = opportunity_service(session)
        payload = Opportunity(
            title="Dup Internship",
            opportunity_type=OpportunityType.SUMMER_INTERNSHIP,
            source_id=source.id,
            url="https://example.edu/jobs/dup",
            fingerprint="",
            organization_id=source.organization_id,
        )
        await service.create(payload)
        with pytest.raises(DuplicateEntityError):
            await service.create(
                Opportunity(
                    title="Dup Internship",
                    opportunity_type=OpportunityType.SUMMER_INTERNSHIP,
                    source_id=source.id,
                    url="https://example.edu/jobs/dup",
                    fingerprint="",
                    organization_id=source.organization_id,
                )
            )

    async def test_create_bad_source_raises(self, session):
        service = opportunity_service(session)
        with pytest.raises(ValidationError):
            await service.create(
                Opportunity(
                    title="No Source",
                    opportunity_type=OpportunityType.SUMMER_INTERNSHIP,
                    source_id=777777,
                    url="https://example.edu/jobs/x",
                    fingerprint="",
                )
            )

    async def test_list_pagination_total(self, session):
        source = await self._setup(session)
        service = opportunity_service(session)
        for i in range(3):
            await service.create(
                Opportunity(
                    title=f"Role {i}",
                    opportunity_type=OpportunityType.RESEARCH_INTERNSHIP,
                    source_id=source.id,
                    url=f"https://example.edu/jobs/{i}",
                    fingerprint="",
                    organization_id=source.organization_id,
                )
            )
        page = await service.list_active(limit=2, offset=0)
        assert page.total >= 3
        assert len(page.items) == 2
        assert page.has_more is True

    async def test_deactivate(self, session):
        source = await self._setup(session)
        service = opportunity_service(session)
        opp = await service.create(
            Opportunity(
                title="To Deactivate",
                opportunity_type=OpportunityType.RESEARCH_INTERNSHIP,
                source_id=source.id,
                url="https://example.edu/jobs/deact",
                fingerprint="",
                organization_id=source.organization_id,
            )
        )
        deactivated = await service.deactivate(opp.id)
        assert deactivated.is_active is False

    async def test_get_missing_raises(self, session):
        service = opportunity_service(session)
        with pytest.raises(EntityNotFoundError):
            await service.get(424242)
