from app.domain.entities.opportunity_match import OpportunityMatch
from app.infrastructure.db.opportunity_match_model import OpportunityMatchModel


def to_entity(m: OpportunityMatchModel) -> OpportunityMatch:
    return OpportunityMatch(
        id=m.id,
        profile_id=m.profile_id,
        opportunity_id=m.opportunity_id,
        match_score=m.match_score,
        match_rationale=m.match_rationale or "",
        is_saved=m.is_saved,
        is_applied=m.is_applied,
        applied_at=m.applied_at,
        application_notes=m.application_notes or "",
        is_notified=m.is_notified,
        notified_at=m.notified_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: OpportunityMatch) -> OpportunityMatchModel:
    return OpportunityMatchModel(
        id=e.id,
        profile_id=e.profile_id,
        opportunity_id=e.opportunity_id,
        match_score=e.match_score,
        match_rationale=e.match_rationale,
        is_saved=e.is_saved,
        is_applied=e.is_applied,
        applied_at=e.applied_at,
        application_notes=e.application_notes,
        is_notified=e.is_notified,
        notified_at=e.notified_at,
    )


def apply_to_model(e: OpportunityMatch, m: OpportunityMatchModel) -> None:
    m.match_score = e.match_score
    m.match_rationale = e.match_rationale
    m.is_saved = e.is_saved
    m.is_applied = e.is_applied
    m.applied_at = e.applied_at
    m.application_notes = e.application_notes
    m.is_notified = e.is_notified
    m.notified_at = e.notified_at
