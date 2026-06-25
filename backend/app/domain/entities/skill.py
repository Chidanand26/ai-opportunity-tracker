from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import SkillCategory


@dataclass
class Skill:
    """
    A normalised, deduplicated skill tag.

    `aliases` allows the system to map "ML", "Machine Learning", and
    "machine-learning" to the same canonical skill without losing the
    original surface form from scraped postings.
    """

    name: str
    category: SkillCategory

    id: int | None = None
    aliases: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __str__(self) -> str:
        return self.name
