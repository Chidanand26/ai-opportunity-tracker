"""Pagination data transfer objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Page[T]:
    """A single page of results plus the metadata needed to paginate.

    Uses PEP 695 native generics (Python 3.12+).

    Attributes:
        items: The records on this page.
        total: Total number of records matching the query (across all pages).
        limit: Maximum number of records requested for this page.
        offset: Number of records skipped before this page.
    """

    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Whether more records exist after this page."""
        return self.offset + len(self.items) < self.total
