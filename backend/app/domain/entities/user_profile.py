from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import DegreeLevel, NotificationFrequency, OpportunityType


@dataclass
class ProfileSkill:
    """Junction record: a skill the user has, with their self-assessed proficiency."""
    from app.domain.enums import ProficiencyLevel
    skill_id: int
    proficiency_level: ProficiencyLevel


@dataclass
class UserProfile:
    """
    The single user's profile in the MVP.

    Design for multi-user: every field here is user-scoped.
    When multi-user is needed:
    1. Add a `users` table.
    2. Remove the `user_id: int = 1` default.
    3. Wire authentication — services already accept user_id as a parameter.

    `preferred_opportunity_types` and `preferred_locations` drive the
    pre-filter stage of the matching pipeline (cheap, no LLM call).
    `min_match_score_for_email` gates which matches trigger notifications.
    """

    display_name: str
    email: str

    id: int | None = None
    user_id: int = 1                # FK to future users table; always 1 in MVP
    bio: str = ""
    degree_level: DegreeLevel = DegreeLevel.MASTERS
    graduation_year: int | None = None
    gpa: float | None = None
    current_institution: str = ""
    research_interests: str = ""
    preferred_locations: list[str] = field(default_factory=list)   # city/country names
    preferred_opportunity_types: list[OpportunityType] = field(default_factory=list)
    min_stipend_usd: float | None = None
    cv_url: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    # Notification preferences
    notification_email_enabled: bool = True
    notification_frequency: NotificationFrequency = NotificationFrequency.DAILY_DIGEST
    min_match_score_for_email: int = 70   # 0-100; only email if score ≥ this
    created_at: datetime | None = None
    updated_at: datetime | None = None
