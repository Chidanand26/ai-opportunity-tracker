from dataclasses import dataclass

from app.domain.enums import LocationType


@dataclass(frozen=True)
class Location:
    """Structured location for an opportunity."""

    location_type: LocationType = LocationType.NOT_SPECIFIED
    city: str = ""
    country: str = ""
    region: str = ""    # state / province

    @classmethod
    def remote(cls) -> "Location":
        return cls(location_type=LocationType.REMOTE)

    @classmethod
    def on_site(cls, city: str = "", country: str = "", region: str = "") -> "Location":
        return cls(location_type=LocationType.ON_SITE, city=city, country=country, region=region)

    def display(self) -> str:
        if self.location_type == LocationType.REMOTE:
            return "Remote"
        parts = [p for p in [self.city, self.region, self.country] if p]
        label = ", ".join(parts) if parts else "Location not specified"
        if self.location_type == LocationType.HYBRID:
            label += " (Hybrid)"
        return label
