"""
Integration tests for all repository implementations.
Requires PostgreSQL (docker compose up -d db).
Each test rolls back its transaction — no data persists between tests.
"""

import pytest

from app.domain.entities.notification import Notification
from app.domain.entities.opportunity import Opportunity
from app.domain.entities.opportunity_match import OpportunityMatch
from app.domain.entities.organization import Organization
from app.domain.entities.professor import Professor
from app.domain.entities.scrape_job import ScrapeJob
from app.domain.entities.scrape_result import ScrapeResult
from app.domain.entities.skill import Skill
from app.domain.entities.source import Source
from app.domain.entities.user_profile import UserProfile
from app.domain.enums import (
    DegreeLevel,
    LocationType,
    NotificationChannel,
    NotificationType,
    OpportunityType,
    OrganizationType,
    ScrapeStatus,
    SkillCategory,
    SourceType,
)
from app.infrastructure.db.repositories.notification_repository import (
    SqlAlchemyNotificationRepository,
)
from app.infrastructure.db.repositories.opportunity_match_repository import (
    SqlAlchemyOpportunityMatchRepository,
)
from app.infrastructure.db.repositories.opportunity_repository import (
    SqlAlchemyOpportunityRepository,
)
from app.infrastructure.db.repositories.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.db.repositories.professor_repository import (
    SqlAlchemyProfessorRepository,
)
from app.infrastructure.db.repositories.scrape_job_repository import (
    SqlAlchemyScrapeJobRepository,
)
from app.infrastructure.db.repositories.skill_repository import SqlAlchemySkillRepository
from app.infrastructure.db.repositories.source_repository import SqlAlchemySourceRepository
from app.infrastructure.db.repositories.user_profile_repository import (
    SqlAlchemyUserProfileRepository,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_org(name: str = "Test University") -> Organization:
    return Organization(name=name, org_type=OrganizationType.UNIVERSITY, country="USA")


def make_source(org_id: int | None = None, name: str = "Test Source") -> Source:
    return Source(
        name=name,
        url=f"https://example.edu/{name.lower().replace(' ', '-')}",
        source_type=SourceType.UNIVERSITY_PORTAL,
        adapter_class="rss_feed",
        organization_id=org_id,
    )


def make_opportunity(source_id: int, fingerprint: str = "abc123def456abcd") -> Opportunity:
    return Opportunity(
        title="ML Research Internship",
        opportunity_type=OpportunityType.RESEARCH_INTERNSHIP,
        source_id=source_id,
        url="https://lab.edu/intern",
        fingerprint=fingerprint,
        description="Join our NLP lab.",
        is_active=True,
    )


def make_profile(email: str = "alice@example.com") -> UserProfile:
    return UserProfile(
        display_name="Alice",
        email=email,
        degree_level=DegreeLevel.MASTERS,
    )


# ── Organization ──────────────────────────────────────────────────────────────


class TestOrganizationRepository:
    async def test_save_and_get_by_id(self, session):
        repo = SqlAlchemyOrganizationRepository(session)
        saved = await repo.save(make_org("MIT"))
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.name == "MIT"
        assert fetched.org_type == OrganizationType.UNIVERSITY

    async def test_get_by_name(self, session):
        repo = SqlAlchemyOrganizationRepository(session)
        await repo.save(make_org("Stanford"))
        result = await repo.get_by_name("Stanford")
        assert result is not None
        assert result.name == "Stanford"

    async def test_get_by_name_returns_none_for_unknown(self, session):
        repo = SqlAlchemyOrganizationRepository(session)
        result = await repo.get_by_name("Nonexistent University")
        assert result is None

    async def test_update(self, session):
        repo = SqlAlchemyOrganizationRepository(session)
        saved = await repo.save(make_org("Caltech"))
        saved.city = "Pasadena"
        updated = await repo.update(saved)
        assert updated.city == "Pasadena"

    async def test_list_all(self, session):
        repo = SqlAlchemyOrganizationRepository(session)
        await repo.save(make_org("OrgA"))
        await repo.save(make_org("OrgB"))
        results = await repo.list_all()
        names = [o.name for o in results]
        assert "OrgA" in names
        assert "OrgB" in names

    async def test_search(self, session):
        repo = SqlAlchemyOrganizationRepository(session)
        await repo.save(make_org("Harvard University"))
        await repo.save(make_org("Princeton University"))
        results = await repo.search("Harvard")
        assert len(results) >= 1
        assert any(o.name == "Harvard University" for o in results)


# ── Source ────────────────────────────────────────────────────────────────────


class TestSourceRepository:
    async def _saved_org(self, session) -> Organization:
        return await SqlAlchemyOrganizationRepository(session).save(make_org())

    async def test_save_and_get_by_id(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemySourceRepository(session)
        saved = await repo.save(make_source(org_id=org.id))
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.source_type == SourceType.UNIVERSITY_PORTAL

    async def test_get_all_active(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemySourceRepository(session)
        s = make_source(org_id=org.id)
        s.is_active = True
        await repo.save(s)
        results = await repo.get_all_active()
        assert len(results) >= 1
        assert all(r.is_active for r in results)

    async def test_touch_last_scraped(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemySourceRepository(session)
        saved = await repo.save(make_source(org_id=org.id))
        assert saved.last_scraped_at is None
        await repo.touch_last_scraped(saved.id)
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.last_scraped_at is not None

    async def test_update(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemySourceRepository(session)
        saved = await repo.save(make_source(org_id=org.id))
        saved.scrape_frequency_hours = 6
        updated = await repo.update(saved)
        assert updated.scrape_frequency_hours == 6


# ── Opportunity ───────────────────────────────────────────────────────────────


class TestOpportunityRepository:
    async def _saved_source(self, session) -> Source:
        org = await SqlAlchemyOrganizationRepository(session).save(make_org())
        return await SqlAlchemySourceRepository(session).save(make_source(org_id=org.id))

    async def test_save_and_get_by_id(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        saved = await repo.save(make_opportunity(source.id))
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.title == "ML Research Internship"

    async def test_get_by_fingerprint(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        fp = "unique1234567890"
        await repo.save(make_opportunity(source.id, fingerprint=fp))
        result = await repo.get_by_fingerprint(fp)
        assert result is not None
        assert result.fingerprint == fp

    async def test_get_by_fingerprint_returns_none_for_unknown(self, session):
        repo = SqlAlchemyOpportunityRepository(session)
        result = await repo.get_by_fingerprint("doesnotexist1234")
        assert result is None

    async def test_list_active(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        await repo.save(make_opportunity(source.id, fingerprint="fp1111111111aaaa"))
        await repo.save(make_opportunity(source.id, fingerprint="fp2222222222bbbb"))
        results = await repo.list_active()
        assert len(results) >= 2

    async def test_list_active_filters_by_type(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        opp = make_opportunity(source.id, fingerprint="fp3333333333cccc")
        opp.opportunity_type = OpportunityType.FELLOWSHIP
        await repo.save(opp)
        results = await repo.list_active(opportunity_type=OpportunityType.FELLOWSHIP)
        assert all(r.opportunity_type == OpportunityType.FELLOWSHIP for r in results)

    async def test_count_active(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        before = await repo.count_active()
        await repo.save(make_opportunity(source.id, fingerprint="fp4444444444dddd"))
        after = await repo.count_active()
        assert after == before + 1

    async def test_search(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        opp = make_opportunity(source.id, fingerprint="fp5555555555eeee")
        opp.title = "Unique XYZ Research Position"
        await repo.save(opp)
        results = await repo.search("XYZ")
        assert len(results) >= 1
        assert any("XYZ" in r.title for r in results)

    async def test_update(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        saved = await repo.save(make_opportunity(source.id, fingerprint="fp6666666666ffff"))
        saved.summary = "AI-generated summary text."
        updated = await repo.update(saved)
        assert updated.summary == "AI-generated summary text."

    async def test_mark_inactive_by_source(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyOpportunityRepository(session)
        o1 = await repo.save(make_opportunity(source.id, fingerprint="fp7777777777gggg"))
        o2 = await repo.save(make_opportunity(source.id, fingerprint="fp8888888888hhhh"))
        count = await repo.mark_inactive_by_source(source.id, except_ids=[o1.id])
        assert count == 1
        fetched = await repo.get_by_id(o2.id)
        assert fetched is not None
        assert fetched.is_active is False


# ── ScrapeJob ─────────────────────────────────────────────────────────────────


class TestScrapeJobRepository:
    async def _saved_source(self, session) -> Source:
        org = await SqlAlchemyOrganizationRepository(session).save(make_org())
        return await SqlAlchemySourceRepository(session).save(make_source(org_id=org.id))

    async def test_save_and_get_by_id(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyScrapeJobRepository(session)
        job = ScrapeJob(source_id=source.id, status=ScrapeStatus.PENDING)
        saved = await repo.save(job)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.status == ScrapeStatus.PENDING

    async def test_update_status(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyScrapeJobRepository(session)
        saved = await repo.save(ScrapeJob(source_id=source.id))
        saved.status = ScrapeStatus.SUCCESS
        saved.opportunities_new = 5
        updated = await repo.update(saved)
        assert updated.status == ScrapeStatus.SUCCESS
        assert updated.opportunities_new == 5

    async def test_list_recent(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyScrapeJobRepository(session)
        await repo.save(ScrapeJob(source_id=source.id))
        await repo.save(ScrapeJob(source_id=source.id))
        results = await repo.list_recent(source_id=source.id)
        assert len(results) >= 2

    async def test_save_and_list_results(self, session):
        source = await self._saved_source(session)
        repo = SqlAlchemyScrapeJobRepository(session)
        job = await repo.save(ScrapeJob(source_id=source.id))
        r = ScrapeResult(
            scrape_job_id=job.id,
            raw_url="https://example.edu/pos/1",
            fingerprint="result1111111111",
            was_duplicate=True,
        )
        saved_r = await repo.save_result(r)
        assert saved_r.id is not None
        results = await repo.list_results(job.id)
        assert len(results) == 1
        assert results[0].was_duplicate is True


# ── Skill ─────────────────────────────────────────────────────────────────────


class TestSkillRepository:
    async def test_save_and_get(self, session):
        repo = SqlAlchemySkillRepository(session)
        skill = Skill(name="PyTorch", category=SkillCategory.FRAMEWORK)
        saved = await repo.save(skill)
        assert saved.id is not None
        fetched = await repo.get_by_name("PyTorch")
        assert fetched is not None
        assert fetched.category == SkillCategory.FRAMEWORK

    async def test_get_or_create_creates_once(self, session):
        repo = SqlAlchemySkillRepository(session)
        s1 = await repo.get_or_create("Rust", SkillCategory.PROGRAMMING)
        s2 = await repo.get_or_create("Rust", SkillCategory.PROGRAMMING)
        assert s1.id == s2.id

    async def test_list_all(self, session):
        repo = SqlAlchemySkillRepository(session)
        await repo.save(Skill(name="Docker", category=SkillCategory.TOOL))
        skills = await repo.list_all()
        assert any(s.name == "Docker" for s in skills)


# ── UserProfile ───────────────────────────────────────────────────────────────


class TestUserProfileRepository:
    async def test_save_and_get_by_id(self, session):
        repo = SqlAlchemyUserProfileRepository(session)
        saved = await repo.save(make_profile())
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.email == "alice@example.com"

    async def test_get_by_user_id(self, session):
        repo = SqlAlchemyUserProfileRepository(session)
        saved = await repo.save(make_profile("bob@example.com"))
        result = await repo.get_by_user_id(saved.user_id)
        assert result is not None

    async def test_update(self, session):
        repo = SqlAlchemyUserProfileRepository(session)
        saved = await repo.save(make_profile("carol@example.com"))
        saved.research_interests = "Computer vision"
        updated = await repo.update(saved)
        assert updated.research_interests == "Computer vision"


# ── Professor ─────────────────────────────────────────────────────────────────


class TestProfessorRepository:
    async def _saved_org(self, session) -> Organization:
        return await SqlAlchemyOrganizationRepository(session).save(make_org())

    async def test_save_and_get(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemyProfessorRepository(session)
        prof = Professor(
            name="Dr. Ada Lovelace",
            organization_id=org.id,
            department="CS",
            is_accepting_students=True,
            research_areas=["NLP", "ML"],
        )
        saved = await repo.save(prof)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.name == "Dr. Ada Lovelace"
        assert fetched.research_areas == ["NLP", "ML"]

    async def test_list_accepting_students(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemyProfessorRepository(session)
        p1 = Professor(name="Prof A", organization_id=org.id, is_accepting_students=True)
        p2 = Professor(name="Prof B", organization_id=org.id, is_accepting_students=False)
        await repo.save(p1)
        await repo.save(p2)
        results = await repo.list_accepting_students()
        assert all(p.is_accepting_students is True for p in results)

    async def test_get_by_organization(self, session):
        org = await self._saved_org(session)
        repo = SqlAlchemyProfessorRepository(session)
        await repo.save(Professor(name="Prof X", organization_id=org.id))
        await repo.save(Professor(name="Prof Y", organization_id=org.id))
        results = await repo.get_by_organization(org.id)
        assert len(results) >= 2


# ── OpportunityMatch ──────────────────────────────────────────────────────────


class TestOpportunityMatchRepository:
    async def _setup(self, session):
        org = await SqlAlchemyOrganizationRepository(session).save(make_org())
        source = await SqlAlchemySourceRepository(session).save(make_source(org_id=org.id))
        opp = await SqlAlchemyOpportunityRepository(session).save(
            make_opportunity(source.id, fingerprint="matchtest1111111")
        )
        profile = await SqlAlchemyUserProfileRepository(session).save(
            make_profile("match@example.com")
        )
        return profile, opp

    async def test_save_and_get(self, session):
        profile, opp = await self._setup(session)
        repo = SqlAlchemyOpportunityMatchRepository(session)
        match = OpportunityMatch(
            profile_id=profile.id,
            opportunity_id=opp.id,
            match_score=85,
            match_rationale="Great fit.",
        )
        saved = await repo.save(match)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.match_score == 85

    async def test_get_by_profile_and_opportunity(self, session):
        profile, opp = await self._setup(session)
        repo = SqlAlchemyOpportunityMatchRepository(session)
        await repo.save(OpportunityMatch(
            profile_id=profile.id, opportunity_id=opp.id, match_score=70
        ))
        result = await repo.get_by_profile_and_opportunity(profile.id, opp.id)
        assert result is not None
        assert result.match_score == 70

    async def test_list_by_profile_min_score(self, session):
        profile, opp = await self._setup(session)
        repo = SqlAlchemyOpportunityMatchRepository(session)
        await repo.save(OpportunityMatch(
            profile_id=profile.id, opportunity_id=opp.id, match_score=90
        ))
        results = await repo.list_by_profile(profile.id, min_score=80)
        assert all(r.match_score >= 80 for r in results)

    async def test_list_unnotified_above_threshold(self, session):
        profile, opp = await self._setup(session)
        repo = SqlAlchemyOpportunityMatchRepository(session)
        m = OpportunityMatch(
            profile_id=profile.id, opportunity_id=opp.id,
            match_score=88, is_notified=False,
        )
        await repo.save(m)
        results = await repo.list_unnotified_above_threshold(profile.id, min_score=70)
        assert len(results) >= 1
        assert all(not r.is_notified for r in results)

    async def test_update_marks_notified(self, session):
        profile, opp = await self._setup(session)
        repo = SqlAlchemyOpportunityMatchRepository(session)
        saved = await repo.save(OpportunityMatch(
            profile_id=profile.id, opportunity_id=opp.id, match_score=75
        ))
        saved.is_notified = True
        updated = await repo.update(saved)
        assert updated.is_notified is True


# ── Notification ──────────────────────────────────────────────────────────────


class TestNotificationRepository:
    async def _saved_profile(self, session) -> UserProfile:
        return await SqlAlchemyUserProfileRepository(session).save(
            make_profile("notif@example.com")
        )

    async def test_save_and_get(self, session):
        profile = await self._saved_profile(session)
        repo = SqlAlchemyNotificationRepository(session)
        n = Notification(
            profile_id=profile.id,
            notification_type=NotificationType.NEW_MATCH,
            channel=NotificationChannel.EMAIL,
            subject="New match",
            body="You have a new opportunity match.",
        )
        saved = await repo.save(n)
        assert saved.id is not None
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.subject == "New match"

    async def test_list_by_profile(self, session):
        profile = await self._saved_profile(session)
        repo = SqlAlchemyNotificationRepository(session)
        for i in range(3):
            await repo.save(Notification(
                profile_id=profile.id,
                notification_type=NotificationType.DIGEST,
                channel=NotificationChannel.EMAIL,
                subject=f"Digest {i}",
                body="Weekly digest.",
            ))
        results = await repo.list_by_profile(profile.id)
        assert len(results) >= 3

    async def test_list_unsent(self, session):
        profile = await self._saved_profile(session)
        repo = SqlAlchemyNotificationRepository(session)
        await repo.save(Notification(
            profile_id=profile.id,
            notification_type=NotificationType.NEW_MATCH,
            channel=NotificationChannel.EMAIL,
            subject="Unsent",
            body="Not sent yet.",
            # sent_at is None by default
        ))
        results = await repo.list_unsent()
        assert len(results) >= 1
        assert all(r.sent_at is None for r in results)

    async def test_mark_read(self, session):
        profile = await self._saved_profile(session)
        repo = SqlAlchemyNotificationRepository(session)
        saved = await repo.save(Notification(
            profile_id=profile.id,
            notification_type=NotificationType.NEW_MATCH,
            channel=NotificationChannel.IN_APP,
            subject="Unread",
            body="Mark me read.",
        ))
        assert saved.is_read is False
        await repo.mark_read(saved.id)
        fetched = await repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.is_read is True
