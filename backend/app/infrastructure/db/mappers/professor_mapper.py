from app.domain.entities.professor import Professor
from app.infrastructure.db.professor_model import ProfessorModel


def to_entity(m: ProfessorModel) -> Professor:
    return Professor(
        id=m.id,
        name=m.name,
        organization_id=m.organization_id,
        email=m.email or "",
        profile_url=m.profile_url or "",
        department=m.department or "",
        lab_name=m.lab_name or "",
        research_areas=list(m.research_areas or []),
        bio=m.bio or "",
        is_accepting_students=m.is_accepting_students,
        google_scholar_url=m.google_scholar_url or "",
        metadata=dict(m.metadata_ or {}),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: Professor) -> ProfessorModel:
    return ProfessorModel(
        id=e.id,
        name=e.name,
        organization_id=e.organization_id,
        email=e.email,
        profile_url=e.profile_url,
        department=e.department,
        lab_name=e.lab_name,
        research_areas=e.research_areas,
        bio=e.bio,
        is_accepting_students=e.is_accepting_students,
        google_scholar_url=e.google_scholar_url,
        metadata_=e.metadata,
    )


def apply_to_model(e: Professor, m: ProfessorModel) -> None:
    m.name = e.name
    m.organization_id = e.organization_id
    m.email = e.email
    m.profile_url = e.profile_url
    m.department = e.department
    m.lab_name = e.lab_name
    m.research_areas = e.research_areas
    m.bio = e.bio
    m.is_accepting_students = e.is_accepting_students
    m.google_scholar_url = e.google_scholar_url
    m.metadata_ = e.metadata
