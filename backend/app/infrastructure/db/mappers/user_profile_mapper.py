from app.domain.entities.user_profile import UserProfile
from app.domain.enums import DegreeLevel, NotificationFrequency, OpportunityType
from app.infrastructure.db.user_profile_model import UserProfileModel


def to_entity(m: UserProfileModel) -> UserProfile:
    return UserProfile(
        id=m.id,
        user_id=m.user_id,
        display_name=m.display_name,
        email=m.email,
        bio=m.bio or "",
        degree_level=DegreeLevel(m.degree_level),
        graduation_year=m.graduation_year,
        gpa=m.gpa,
        current_institution=m.current_institution or "",
        research_interests=m.research_interests or "",
        preferred_locations=list(m.preferred_locations or []),
        preferred_opportunity_types=[
            OpportunityType(t) for t in (m.preferred_opportunity_types or [])
        ],
        min_stipend_usd=m.min_stipend_usd,
        cv_url=m.cv_url or "",
        linkedin_url=m.linkedin_url or "",
        github_url=m.github_url or "",
        notification_email_enabled=m.notification_email_enabled,
        notification_frequency=NotificationFrequency(m.notification_frequency),
        min_match_score_for_email=m.min_match_score_for_email,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: UserProfile) -> UserProfileModel:
    return UserProfileModel(
        id=e.id,
        user_id=e.user_id,
        display_name=e.display_name,
        email=e.email,
        bio=e.bio,
        degree_level=str(e.degree_level),
        graduation_year=e.graduation_year,
        gpa=e.gpa,
        current_institution=e.current_institution,
        research_interests=e.research_interests,
        preferred_locations=e.preferred_locations,
        preferred_opportunity_types=[str(t) for t in e.preferred_opportunity_types],
        min_stipend_usd=e.min_stipend_usd,
        cv_url=e.cv_url,
        linkedin_url=e.linkedin_url,
        github_url=e.github_url,
        notification_email_enabled=e.notification_email_enabled,
        notification_frequency=str(e.notification_frequency),
        min_match_score_for_email=e.min_match_score_for_email,
    )


def apply_to_model(e: UserProfile, m: UserProfileModel) -> None:
    m.display_name = e.display_name
    m.email = e.email
    m.bio = e.bio
    m.degree_level = str(e.degree_level)
    m.graduation_year = e.graduation_year
    m.gpa = e.gpa
    m.current_institution = e.current_institution
    m.research_interests = e.research_interests
    m.preferred_locations = e.preferred_locations
    m.preferred_opportunity_types = [str(t) for t in e.preferred_opportunity_types]
    m.min_stipend_usd = e.min_stipend_usd
    m.cv_url = e.cv_url
    m.linkedin_url = e.linkedin_url
    m.github_url = e.github_url
    m.notification_email_enabled = e.notification_email_enabled
    m.notification_frequency = str(e.notification_frequency)
    m.min_match_score_for_email = e.min_match_score_for_email
