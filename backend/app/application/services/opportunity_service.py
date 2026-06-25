"""Application service for opportunities."""

from app.application.dto.pagination import Page
from app.application.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.entities.opportunity import Opportunity
from app.domain.enums import OpportunityType
from app.domain.ports.opportunity_repository import OpportunityRepository
from app.domain.ports.organization_repository import OrganizationRepository
from app.domain.ports.source_repository import SourceRepository
from app.domain.value_objects.fingerprint import Fingerprint


class OpportunityService:
    """Use cases for reading and writing opportunities.

    The scraper pipeline persists opportunities directly through the repository;
    this service covers the API-driven and manual paths, adding fingerprint
    generation, duplicate detection, referential validation, and paginated
    listing on top of the repository.
    """

    def __init__(
        self,
        opportunities: OpportunityRepository,
        sources: SourceRepository,
        organizations: OrganizationRepository,
    ) -> None:
        self._opportunities = opportunities
        self._sources = sources
        self._organizations = organizations

    async def get(self, opportunity_id: int) -> Opportunity:
        """Return an opportunity by id.

        Args:
            opportunity_id: Primary key of the opportunity.

        Returns:
            The matching opportunity.

        Raises:
            EntityNotFoundError: If no opportunity has that id.
        """
        opportunity = await self._opportunities.get_by_id(opportunity_id)
        if opportunity is None:
            raise EntityNotFoundError("Opportunity", opportunity_id)
        return opportunity

    async def list_active(
        self,
        limit: int = 50,
        offset: int = 0,
        opportunity_type: OpportunityType | None = None,
        organization_id: int | None = None,
    ) -> Page[Opportunity]:
        """Return a paginated, optionally filtered page of active opportunities.

        Args:
            limit: Maximum number of records on the page.
            offset: Number of records to skip.
            opportunity_type: Restrict to a single opportunity type.
            organization_id: Restrict to a single organization.

        Returns:
            A :class:`Page` whose ``total`` reflects the same filters.
        """
        items = await self._opportunities.list_active(
            limit=limit,
            offset=offset,
            opportunity_type=opportunity_type,
            organization_id=organization_id,
        )
        total = await self._opportunities.count_active(
            opportunity_type=opportunity_type,
            organization_id=organization_id,
        )
        return Page(items=items, total=total, limit=limit, offset=offset)

    async def search(self, query: str, limit: int = 50) -> list[Opportunity]:
        """Full-text-style search over active opportunities.

        Args:
            query: Case-insensitive substring matched against title,
                description, and requirements.
            limit: Maximum number of results.

        Returns:
            Matching opportunities, most recent first.
        """
        return await self._opportunities.search(query, limit=limit)

    async def create(self, opportunity: Opportunity) -> Opportunity:
        """Create an opportunity, generating its fingerprint if absent.

        Args:
            opportunity: The opportunity to persist. ``id`` is ignored; if
                ``fingerprint`` is empty it is derived from the title, the
                resolved organization name, and the url.

        Returns:
            The persisted opportunity with its generated id.

        Raises:
            ValidationError: If ``source_id`` does not reference a row, or a set
                ``organization_id`` does not reference a row.
            DuplicateEntityError: If an opportunity with the same fingerprint
                already exists.
        """
        if await self._sources.get_by_id(opportunity.source_id) is None:
            raise ValidationError(f"Source {opportunity.source_id} does not exist")

        organization_name = await self._resolve_organization_name(opportunity.organization_id)

        if not opportunity.fingerprint:
            opportunity.fingerprint = Fingerprint.generate(
                title=opportunity.title,
                organization_name=organization_name,
                url=opportunity.url,
            ).value

        existing = await self._opportunities.get_by_fingerprint(opportunity.fingerprint)
        if existing is not None:
            raise DuplicateEntityError("Opportunity", "fingerprint", opportunity.fingerprint)

        return await self._opportunities.save(opportunity)

    async def update(self, opportunity: Opportunity) -> Opportunity:
        """Update an existing opportunity.

        Args:
            opportunity: Opportunity carrying the id and new field values.

        Returns:
            The updated opportunity.

        Raises:
            EntityNotFoundError: If the opportunity does not exist.
        """
        if opportunity.id is None or await self._opportunities.get_by_id(opportunity.id) is None:
            raise EntityNotFoundError("Opportunity", opportunity.id)
        return await self._opportunities.update(opportunity)

    async def deactivate(self, opportunity_id: int) -> Opportunity:
        """Mark an opportunity inactive (soft delete).

        Args:
            opportunity_id: Opportunity to deactivate.

        Returns:
            The updated, inactive opportunity.

        Raises:
            EntityNotFoundError: If the opportunity does not exist.
        """
        opportunity = await self.get(opportunity_id)
        opportunity.is_active = False
        return await self._opportunities.update(opportunity)

    async def _resolve_organization_name(self, organization_id: int | None) -> str:
        """Return the organization's name, or ``""`` when none is referenced.

        Raises:
            ValidationError: If a non-null ``organization_id`` does not exist.
        """
        if organization_id is None:
            return ""
        organization = await self._organizations.get_by_id(organization_id)
        if organization is None:
            raise ValidationError(f"Organization {organization_id} does not exist")
        return organization.name
