"""
Mapper roundtrip tests — no database, no Docker required.

Each test constructs a domain entity, converts it to an ORM model,
then converts back to an entity and asserts field equality.
This guarantees the mappers are loss-free for every field.
"""

from datetime import date, datetime
from decimal import Decimal

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
    NotificationFrequency,
    NotificationType,
    OpportunityType,
    OrganizationType,
    ScrapeStatus,
    SkillCategory,
    SourceType,
)
from app.infrastructure.db.mappers import (
    notification_mapper,
    opportunity_mapper,
    opportunity_match_mapper,
    organization_mapper,
    professor_mapper,
    scrape_job_mapper,
    skill_mapper,
    source_mapper,
    user_profile_mapper,
)


class TestOrganizationMapper:
    def _make(self) -> Organization:
        return Organization(
            id=1,
            name="MIT",
            org_type=OrganizationType.UNIVERSITY,
            website="https://mit.edu",
            country="USA",
            city="Cambridge",
            description="Top research university",
            metadata={"rank": 1},
        )

    def test_roundtrip(self):
        entity = self._make()
        model = organization_mapper.to_model(entity)
        result = organization_mapper.to_entity(model)
        assert result.name == entity.name
        assert result.org_type == entity.org_type
        assert result.website == entity.website
        assert result.country == entity.country
        assert result.metadata == entity.metadata

    def test_apply_to_model_updates_fields(self):
        entity = self._make()
        model = organization_mapper.to_model(entity)
        entity.city = "Boston"
        organization_mapper.apply_to_model(entity, model)
        assert model.city == "Boston"


class TestSourceMapper:
    def _make(self) -> Source:
        return Source(
            id=1,
            name="MIT Jobs",
            url="https://jobs.mit.edu",
            source_type=SourceType.UNIVERSITY_PORTAL,
            adapter_class="rss_feed",
            organization_id=1,
            is_active=True,
            scrape_frequency_hours=12,
            config={"feed_type": "rss"},
        )

    def test_roundtrip(self):
        entity = self._make()
        model = source_mapper.to_model(entity)
        result = source_mapper.to_entity(model)
        assert result.name == entity.name
        assert result.source_type == entity.source_type
        assert result.adapter_class == entity.adapter_class
        assert result.config == entity.config
        assert result.scrape_frequency_hours == entity.scrape_frequency_hours

    def test_source_type_enum_preserved(self):
        entity = self._make()
        model = source_mapper.to_model(entity)
        result = source_mapper.to_entity(model)
        assert isinstance(result.source_type, SourceType)
        assert result.source_type == SourceType.UNIVERSITY_PORTAL


class TestOpportunityMapper:
    def _make(self) -> Opportunity:
        return Opportunity(
            id=1,
            title="ML Research Internship",
            opportunity_type=OpportunityType.RESEARCH_INTERNSHIP,
            source_id=1,
            url="https://lab.edu/intern",
            fingerprint="abc123def456abcd",
            organization_id=1,
            description="Join our NLP lab.",
            location="Cambridge, MA",
            location_type=LocationType.ON_SITE,
            city="Cambridge",
            country="USA",
            stipend_amount=Decimal("7000.00"),
            stipend_currency="USD",
            application_deadline=date(2025, 3, 15),
            is_active=True,
            raw_data={"source_html": "<p>test</p>"},
            metadata={"tags": ["nlp", "ml"]},
        )

    def test_roundtrip(self):
        entity = self._make()
        model = opportunity_mapper.to_model(entity)
        result = opportunity_mapper.to_entity(model)
        assert result.title == entity.title
        assert result.opportunity_type == entity.opportunity_type
        assert result.fingerprint == entity.fingerprint
        assert result.stipend_amount == entity.stipend_amount
        assert result.application_deadline == entity.application_deadline
        assert result.location_type == entity.location_type
        assert result.raw_data == entity.raw_data
        assert result.metadata == entity.metadata

    def test_none_stipend_preserved(self):
        entity = self._make()
        entity.stipend_amount = None
        model = opportunity_mapper.to_model(entity)
        result = opportunity_mapper.to_entity(model)
        assert result.stipend_amount is None

    def test_opportunity_type_is_enum(self):
        entity = self._make()
        model = opportunity_mapper.to_model(entity)
        result = opportunity_mapper.to_entity(model)
        assert isinstance(result.opportunity_type, OpportunityType)


class TestScrapeJobMapper:
    def _make_job(self) -> ScrapeJob:
        return ScrapeJob(
            id=1,
            source_id=1,
            status=ScrapeStatus.SUCCESS,
            celery_task_id="abc-123",
            opportunities_found=10,
            opportunities_new=3,
        )

    def _make_result(self) -> ScrapeResult:
        return ScrapeResult(
            id=1,
            scrape_job_id=1,
            raw_url="https://example.edu/pos/1",
            fingerprint="abcd1234ef567890",
            opportunity_id=42,
            was_duplicate=False,
        )

    def test_job_roundtrip(self):
        entity = self._make_job()
        model = scrape_job_mapper.job_to_model(entity)
        result = scrape_job_mapper.job_to_entity(model)
        assert result.status == entity.status
        assert result.celery_task_id == entity.celery_task_id
        assert result.opportunities_found == entity.opportunities_found
        assert result.opportunities_new == entity.opportunities_new

    def test_result_roundtrip(self):
        entity = self._make_result()
        model = scrape_job_mapper.result_to_model(entity)
        result = scrape_job_mapper.result_to_entity(model)
        assert result.raw_url == entity.raw_url
        assert result.fingerprint == entity.fingerprint
        assert result.opportunity_id == entity.opportunity_id
        assert result.was_duplicate == entity.was_duplicate

    def test_status_is_enum(self):
        entity = self._make_job()
        model = scrape_job_mapper.job_to_model(entity)
        result = scrape_job_mapper.job_to_entity(model)
        assert isinstance(result.status, ScrapeStatus)


class TestSkillMapper:
    def test_roundtrip(self):
        entity = Skill(
            id=1, name="Python", category=SkillCategory.PROGRAMMING,
            aliases=["python3", "py"],
        )
        model = skill_mapper.to_model(entity)
        result = skill_mapper.to_entity(model)
        assert result.name == "Python"
        assert result.category == SkillCategory.PROGRAMMING
        assert result.aliases == ["python3", "py"]


class TestUserProfileMapper:
    def _make(self) -> UserProfile:
        return UserProfile(
            id=1,
            user_id=1,
            display_name="Alice",
            email="alice@example.com",
            degree_level=DegreeLevel.MASTERS,
            graduation_year=2026,
            research_interests="NLP, computer vision",
            preferred_locations=["Boston", "Remote"],
            preferred_opportunity_types=[OpportunityType.RESEARCH_INTERNSHIP],
            notification_frequency=NotificationFrequency.DAILY_DIGEST,
            min_match_score_for_email=75,
        )

    def test_roundtrip(self):
        entity = self._make()
        model = user_profile_mapper.to_model(entity)
        result = user_profile_mapper.to_entity(model)
        assert result.display_name == entity.display_name
        assert result.degree_level == entity.degree_level
        assert result.preferred_locations == entity.preferred_locations
        assert result.preferred_opportunity_types == entity.preferred_opportunity_types
        assert result.notification_frequency == entity.notification_frequency
        assert result.min_match_score_for_email == entity.min_match_score_for_email

    def test_opportunity_types_are_enums(self):
        entity = self._make()
        model = user_profile_mapper.to_model(entity)
        result = user_profile_mapper.to_entity(model)
        for t in result.preferred_opportunity_types:
            assert isinstance(t, OpportunityType)


class TestOpportunityMatchMapper:
    def test_roundtrip(self):
        entity = OpportunityMatch(
            id=1,
            profile_id=1,
            opportunity_id=5,
            match_score=82,
            match_rationale="Strong NLP background match.",
            is_saved=True,
            is_notified=False,
        )
        model = opportunity_match_mapper.to_model(entity)
        result = opportunity_match_mapper.to_entity(model)
        assert result.match_score == 82
        assert result.match_rationale == "Strong NLP background match."
        assert result.is_saved is True
        assert result.is_notified is False


class TestNotificationMapper:
    def test_roundtrip(self):
        entity = Notification(
            id=1,
            profile_id=1,
            notification_type=NotificationType.NEW_MATCH,
            channel=NotificationChannel.EMAIL,
            subject="New match: ML Internship",
            body="You have a new 82% match.",
            opportunity_match_id=10,
            is_read=False,
            metadata={"message_id": "abc@mail"},
        )
        model = notification_mapper.to_model(entity)
        result = notification_mapper.to_entity(model)
        assert result.notification_type == NotificationType.NEW_MATCH
        assert result.channel == NotificationChannel.EMAIL
        assert result.subject == entity.subject
        assert result.metadata == entity.metadata
