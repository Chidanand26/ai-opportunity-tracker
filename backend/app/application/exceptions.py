"""Application-layer exceptions.

These represent use-case-level failures. The API layer maps them to HTTP status
codes (e.g. ``EntityNotFoundError`` -> 404, ``DuplicateEntityError`` -> 409,
``ValidationError`` -> 422). Keeping them here means services stay free of any
HTTP/framework concerns.
"""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for all application-layer errors."""


class EntityNotFoundError(ApplicationError):
    """Raised when a requested entity does not exist.

    Attributes:
        entity: Human-readable entity name (e.g. ``"Organization"``).
        identifier: The lookup value that produced no result.
    """

    def __init__(self, entity: str, identifier: object) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} not found: {identifier!r}")


class DuplicateEntityError(ApplicationError):
    """Raised when creating an entity that would violate a uniqueness rule.

    Attributes:
        entity: Human-readable entity name.
        field: The field whose uniqueness was violated.
        value: The conflicting value.
    """

    def __init__(self, entity: str, field: str, value: object) -> None:
        self.entity = entity
        self.field = field
        self.value = value
        super().__init__(f"{entity} already exists with {field}={value!r}")


class ValidationError(ApplicationError):
    """Raised when input fails a business rule before persistence."""
