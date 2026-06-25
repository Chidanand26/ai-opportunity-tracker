from app.domain.entities.organization import Organization
from app.domain.enums import OrganizationType
from app.infrastructure.db.organization_model import OrganizationModel


def to_entity(m: OrganizationModel) -> Organization:
    return Organization(
        id=m.id,
        name=m.name,
        org_type=OrganizationType(m.org_type),
        website=m.website or "",
        logo_url=m.logo_url or "",
        country=m.country or "",
        city=m.city or "",
        description=m.description or "",
        metadata=dict(m.metadata_ or {}),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: Organization) -> OrganizationModel:
    return OrganizationModel(
        id=e.id,
        name=e.name,
        org_type=str(e.org_type),
        website=e.website,
        logo_url=e.logo_url,
        country=e.country,
        city=e.city,
        description=e.description,
        metadata_=e.metadata,
    )


def apply_to_model(e: Organization, m: OrganizationModel) -> None:
    """Update an existing ORM model in-place; preserves DB-managed fields."""
    m.name = e.name
    m.org_type = str(e.org_type)
    m.website = e.website
    m.logo_url = e.logo_url
    m.country = e.country
    m.city = e.city
    m.description = e.description
    m.metadata_ = e.metadata
