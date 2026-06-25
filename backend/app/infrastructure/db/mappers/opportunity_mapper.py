from app.domain.entities.opportunity import Opportunity
from app.domain.enums import LocationType, OpportunityType
from app.infrastructure.db.opportunity_model import OpportunityModel


def to_entity(m: OpportunityModel) -> Opportunity:
    return Opportunity(
        id=m.id,
        title=m.title,
        opportunity_type=OpportunityType(m.opportunity_type),
        source_id=m.source_id,
        url=m.url,
        fingerprint=m.fingerprint,
        organization_id=m.organization_id,
        professor_id=m.professor_id,
        description=m.description or "",
        summary=m.summary or "",
        location=m.location or "",
        location_type=LocationType(m.location_type),
        city=m.city or "",
        country=m.country or "",
        stipend_amount=m.stipend_amount,
        stipend_currency=m.stipend_currency or "USD",
        application_deadline=m.application_deadline,
        start_date=m.start_date,
        duration_weeks=m.duration_weeks,
        requirements=m.requirements or "",
        is_active=m.is_active,
        raw_data=dict(m.raw_data or {}),
        metadata=dict(m.metadata_ or {}),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: Opportunity) -> OpportunityModel:
    return OpportunityModel(
        id=e.id,
        title=e.title,
        opportunity_type=str(e.opportunity_type),
        source_id=e.source_id,
        url=e.url,
        fingerprint=e.fingerprint,
        organization_id=e.organization_id,
        professor_id=e.professor_id,
        description=e.description,
        summary=e.summary,
        location=e.location,
        location_type=str(e.location_type),
        city=e.city,
        country=e.country,
        stipend_amount=e.stipend_amount,
        stipend_currency=e.stipend_currency,
        application_deadline=e.application_deadline,
        start_date=e.start_date,
        duration_weeks=e.duration_weeks,
        requirements=e.requirements,
        is_active=e.is_active,
        raw_data=e.raw_data,
        metadata_=e.metadata,
    )


def apply_to_model(e: Opportunity, m: OpportunityModel) -> None:
    m.title = e.title
    m.opportunity_type = str(e.opportunity_type)
    m.source_id = e.source_id
    m.url = e.url
    m.fingerprint = e.fingerprint
    m.organization_id = e.organization_id
    m.professor_id = e.professor_id
    m.description = e.description
    m.summary = e.summary
    m.location = e.location
    m.location_type = str(e.location_type)
    m.city = e.city
    m.country = e.country
    m.stipend_amount = e.stipend_amount
    m.stipend_currency = e.stipend_currency
    m.application_deadline = e.application_deadline
    m.start_date = e.start_date
    m.duration_weeks = e.duration_weeks
    m.requirements = e.requirements
    m.is_active = e.is_active
    m.raw_data = e.raw_data
    m.metadata_ = e.metadata
