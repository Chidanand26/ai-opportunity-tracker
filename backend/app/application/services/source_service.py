"""Application service for scrape sources."""

from app.application.exceptions import EntityNotFoundError, ValidationError
from app.domain.entities.source import Source
from app.domain.ports.organization_repository import OrganizationRepository
from app.domain.ports.source_repository import SourceRepository


class SourceService:
    """Use cases for managing the sources the scraper pipeline monitors.

    Validates that an optional ``organization_id`` references a real row before
    persisting, so foreign-key violations surface as clear application errors
    rather than database exceptions.
    """

    def __init__(
        self,
        sources: SourceRepository,
        organizations: OrganizationRepository,
    ) -> None:
        self._sources = sources
        self._organizations = organizations

    async def get(self, source_id: int) -> Source:
        """Return a source by id.

        Args:
            source_id: Primary key of the source.

        Returns:
            The matching source.

        Raises:
            EntityNotFoundError: If no source has that id.
        """
        source = await self._sources.get_by_id(source_id)
        if source is None:
            raise EntityNotFoundError("Source", source_id)
        return source

    async def register(self, source: Source) -> Source:
        """Register a new source.

        Args:
            source: The source to persist. Its ``id`` is ignored.

        Returns:
            The persisted source with its generated id.

        Raises:
            ValidationError: If ``organization_id`` is set but does not exist.
        """
        await self._validate_organization(source.organization_id)
        return await self._sources.save(source)

    async def update(self, source: Source) -> Source:
        """Update an existing source.

        Args:
            source: Source carrying the id and new field values.

        Returns:
            The updated source.

        Raises:
            EntityNotFoundError: If the source does not exist.
            ValidationError: If ``organization_id`` is set but does not exist.
        """
        if source.id is None or await self._sources.get_by_id(source.id) is None:
            raise EntityNotFoundError("Source", source.id)
        await self._validate_organization(source.organization_id)
        return await self._sources.update(source)

    async def set_active(self, source_id: int, is_active: bool) -> Source:
        """Activate or deactivate a source.

        Args:
            source_id: Source to toggle.
            is_active: New active state.

        Returns:
            The updated source.

        Raises:
            EntityNotFoundError: If the source does not exist.
        """
        source = await self.get(source_id)
        source.is_active = is_active
        return await self._sources.update(source)

    async def list_active(self) -> list[Source]:
        """Return all active sources.

        Returns:
            Sources whose ``is_active`` is ``True``.
        """
        return await self._sources.get_all_active()

    async def list_due_for_scrape(self) -> list[Source]:
        """Return active sources whose schedule indicates a scrape is due.

        Returns:
            Sources due for scraping per their ``scrape_frequency_hours``.
        """
        return await self._sources.get_due_for_scrape()

    async def _validate_organization(self, organization_id: int | None) -> None:
        """Raise if a non-null ``organization_id`` does not reference a row."""
        if organization_id is None:
            return
        if await self._organizations.get_by_id(organization_id) is None:
            raise ValidationError(f"Organization {organization_id} does not exist")
