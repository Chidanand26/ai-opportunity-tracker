"""
Central enum definitions for the entire domain.

Using StrEnum (Python 3.11+) so enum values serialize to/from plain strings
cleanly — no `.value` unwrapping needed in JSON or DB queries.
"""

from enum import StrEnum


class OpportunityType(StrEnum):
    RESEARCH_INTERNSHIP = "research_internship"
    SUMMER_INTERNSHIP = "summer_internship"
    RA_POSITION = "ra_position"
    MS_PHD_OPENING = "ms_phd_opening"
    FELLOWSHIP = "fellowship"
    SCHOLARSHIP = "scholarship"
    PROFESSOR_RECRUITMENT = "professor_recruitment"
    COMPANY_INTERNSHIP = "company_internship"


class OrganizationType(StrEnum):
    UNIVERSITY = "university"
    COMPANY = "company"
    RESEARCH_LAB = "research_lab"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    OTHER = "other"


class SourceType(StrEnum):
    UNIVERSITY_PORTAL = "university_portal"
    PROFESSOR_PAGE = "professor_page"
    RESEARCH_LAB = "research_lab"
    COMPANY_PORTAL = "company_portal"
    RSS_FEED = "rss_feed"
    AGGREGATE = "aggregate"
    LINKEDIN = "linkedin"   # best-effort only
    OTHER = "other"


class LocationType(StrEnum):
    REMOTE = "remote"
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    NOT_SPECIFIED = "not_specified"


class DegreeLevel(StrEnum):
    UNDERGRADUATE = "undergraduate"
    MASTERS = "masters"
    PHD = "phd"
    POSTDOC = "postdoc"
    PROFESSIONAL = "professional"


class SkillCategory(StrEnum):
    PROGRAMMING = "programming"
    FRAMEWORK = "framework"
    DOMAIN = "domain"
    SOFT_SKILL = "soft_skill"
    TOOL = "tool"
    LANGUAGE = "language"
    OTHER = "other"


class ProficiencyLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class NotificationFrequency(StrEnum):
    INSTANT = "instant"
    DAILY_DIGEST = "daily_digest"
    WEEKLY_DIGEST = "weekly_digest"


class NotificationType(StrEnum):
    NEW_MATCH = "new_match"
    DEADLINE_REMINDER = "deadline_reminder"
    DIGEST = "digest"
    APPLICATION_REMINDER = "application_reminder"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    IN_APP = "in_app"


class ScrapeStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
