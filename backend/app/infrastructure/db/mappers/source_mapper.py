from app.domain.entities.source import Source
from app.domain.enums import SourceType
from app.infrastructure.db.source_model import SourceModel


def to_entity(m: SourceModel) -> Source:
    return Source(
        id=m.id,
        name=m.name,
        url=m.url,
        source_type=SourceType(m.source_type),
        adapter_class=m.adapter_class,
        organization_id=m.organization_id,
        is_active=m.is_active,
        scrape_frequency_hours=m.scrape_frequency_hours,
        config=dict(m.config or {}),
        last_scraped_at=m.last_scraped_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: Source) -> SourceModel:
    return SourceModel(
        id=e.id,
        name=e.name,
        url=e.url,
        source_type=str(e.source_type),
        adapter_class=e.adapter_class,
        organization_id=e.organization_id,
        is_active=e.is_active,
        scrape_frequency_hours=e.scrape_frequency_hours,
        config=e.config,
        last_scraped_at=e.last_scraped_at,
    )


def apply_to_model(e: Source, m: SourceModel) -> None:
    m.name = e.name
    m.url = e.url
    m.source_type = str(e.source_type)
    m.adapter_class = e.adapter_class
    m.organization_id = e.organization_id
    m.is_active = e.is_active
    m.scrape_frequency_hours = e.scrape_frequency_hours
    m.config = e.config
    m.last_scraped_at = e.last_scraped_at
