import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Fingerprint:
    """
    Deterministic content hash used for deduplication.

    Two postings with the same fingerprint are considered identical regardless
    of when or where they were scraped. Stored in the DB as a 16-char hex string
    (first 64 bits of SHA-256) — collision probability is negligible at our scale.
    """

    value: str

    @classmethod
    def generate(cls, title: str, organization_name: str, url: str) -> "Fingerprint":
        """
        Derive a fingerprint from the three most stable fields of a posting.
        Normalised before hashing so minor formatting differences don't create dupes.
        """
        canonical = "::".join([
            cls._normalize(title),
            cls._normalize(organization_name),
            cls._normalize_url(url),
        ])
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        return cls(value=digest[:16])

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower().strip())

    @staticmethod
    def _normalize_url(url: str) -> str:
        # Strip tracking params and fragments; keep scheme + host + path
        url = url.strip().lower().split("?")[0].split("#")[0]
        return url.rstrip("/")

    def __str__(self) -> str:
        return self.value
