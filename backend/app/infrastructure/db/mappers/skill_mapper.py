from app.domain.entities.skill import Skill
from app.domain.enums import SkillCategory
from app.infrastructure.db.skill_model import SkillModel


def to_entity(m: SkillModel) -> Skill:
    return Skill(
        id=m.id,
        name=m.name,
        category=SkillCategory(m.category),
        aliases=list(m.aliases or []),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def to_model(e: Skill) -> SkillModel:
    return SkillModel(
        id=e.id,
        name=e.name,
        category=str(e.category),
        aliases=e.aliases,
    )
