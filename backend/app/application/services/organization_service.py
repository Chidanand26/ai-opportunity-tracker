"""Application service for organizations."""

from app.application.exceptions import DuplicateEntityError, EntityNotFoundError
from app.domain.entities.organization import Organization
from app.domain.enums import OrganizationType
from app.domain.ports.organization_repository import OrganizationRepository


class OrganizationService:
    """Use cases for managing organizations (universities, companies, labs).

    Depends on the :class:`OrganizationRepository` port, not a concrete
    implementation, so the persistence backend can be swapped without changing
    this service.
    """

    def __init__(self, organizations: OrganizationRepository) -> None:
        self._organizations = organizations

    async def get(self, organization_id: int) -> Organization:
        """Return an organization by id.

        Args:
            organization_id: Primary key of the organization.

        Returns:
            The matching organization.

        Raises:
            EntityNotFoundError: If no organization has that id.
        """
        org = await self._organizations.get_by_id(organization_id)
        if org is None:
            raise EntityNotFoundError("Organization", organization_id)
        return org

    async def create(self, organization: Organization) -> Organization:
        """Create a new organization.

        Args:
            organization: The organization to persist. Its ``id`` is ignored.

        Returns:
            The persisted organization with its generated id.

        Raises:
            DuplicateEntityError: If an organization with the same name exists.
        """
        existing = await self._organizations.get_by_name(organization.name)
        if existing is not None:
            raise DuplicateEntityError("Organization", "name", organization.name)
        return await self._organizations.save(organization)

    async def get_or_create(self, name: str, org_type: OrganizationType) -> Organization:
        """Return the organization with ``name``, creating it if absent.

        This is the deduplicating entry point used by ingestion: many scraped
        postings reference the same institution, and we want exactly one row.

        Args:
            name: Organization name to look up or create.
            org_type: Type to assign if a new organization is created.

        Returns:
            The existing or newly created organization.
        """
        existing = await self._organizations.get_by_name(name)
        if existing is not None:
            return existing
        return await self._organizations.save(Organization(name=name, org_type=org_type))

    async def update(self, organization: Organization) -> Organization:
        """Update an existing organization.

        Args:
            organization: Organization carrying the id and new field values.

        Returns:
            The updated organization.

        Raises:
            EntityNotFoundError: If the organization does not exist.
        """
        if organization.id is None or await self._organizations.get_by_id(organization.id) is None:
            raise EntityNotFoundError("Organization", organization.id)
        return await self._organizations.update(organization)

    async def list_all(self, limit: int = 200) -> list[Organization]:
        """Return organizations ordered by name.

        Args:
            limit: Maximum number of organizations to return.

        Returns:
            A list of organizations.
        """
        return await self._organizations.list_all(limit=limit)

    async def search(self, query: str, limit: int = 50) -> list[Organization]:
        """Search organizations by name or description.

        Args:
            query: Case-insensitive substring to match.
            limit: Maximum number of results.

        Returns:
            Matching organizations.
        """
        return await self._organizations.search(query, limit=limit)
