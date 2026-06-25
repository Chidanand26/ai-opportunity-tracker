from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Professor:
    """
    A faculty member whose page is monitored for RA/research opportunities.

    The `is_accepting_students` flag is updated by the ProfessorSuggesterAgent
    after parsing the professor's webpage. `research_areas` feeds the
    matching score between the user's interests and the professor's work.
    """

    name: str
    organization_id: int

    id: int | None = None
    email: str = ""
    profile_url: str = ""
    department: str = ""
    lab_name: str = ""
    research_areas: list[str] = field(default_factory=list)
    bio: str = ""
    is_accepting_students: bool | None = None   # None = unknown
    google_scholar_url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __str__(self) -> str:
        return f"Prof. {self.name} ({self.department})"
