from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.enums import OrganizationType


@dataclass
class Organization:
    """
    A university, company, research lab, or other institution that posts opportunities.
    Sources and Professors are linked to an Organization.
    """

    name: str
    org_type: OrganizationType

    id: int | None = None
    website: str = ""
    logo_url: str = ""
    country: str = ""
    city: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)  # flexible extra attrs
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __str__(self) -> str:
        return f"{self.name} ({self.org_type})"
