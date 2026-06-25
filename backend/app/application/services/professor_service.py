"""Application service for professors."""

from app.application.exceptions import EntityNotFoundError, ValidationError
from app.domain.entities.professor import Professor
from app.domain.ports.organization_repository import OrganizationRepository
from app.domain.ports.professor_repository import ProfessorRepository


class ProfessorService:
    """Use cases for managing professors.

    A professor always belongs to an organization, so this service validates
    the referenced organization exists before persisting.
    """

    def __init__(
        self,
        professors: ProfessorRepository,
        organizations: OrganizationRepository,
    ) -> None:
        self._professors = professors
        self._organizations = organizations

    async def get(self, professor_id: int) -> Professor:
        """Return a professor by id.

        Args:
            professor_id: Primary key of the professor.

        Returns:
            The matching professor.

        Raises:
            EntityNotFoundError: If no professor has that id.
        """
        professor = await self._professors.get_by_id(professor_id)
        if professor is None:
            raise EntityNotFoundError("Professor", professor_id)
        return professor

    async def create(self, professor: Professor) -> Professor:
        """Create a new professor under an existing organization.

        Args:
            professor: The professor to persist. Its ``id`` is ignored.

        Returns:
            The persisted professor with its generated id.

        Raises:
            ValidationError: If ``organization_id`` does not reference a row.
        """
        await self._require_organization(professor.organization_id)
        return await self._professors.save(professor)

    async def update(self, professor: Professor) -> Professor:
        """Update an existing professor.

        Args:
            professor: Professor carrying the id and new field values.

        Returns:
            The updated professor.

        Raises:
            EntityNotFoundError: If the professor does not exist.
            ValidationError: If ``organization_id`` does not reference a row.
        """
        if professor.id is None or await self._professors.get_by_id(professor.id) is None:
            raise EntityNotFoundError("Professor", professor.id)
        await self._require_organization(professor.organization_id)
        return await self._professors.update(professor)

    async def list_by_organization(self, organization_id: int) -> list[Professor]:
        """Return all professors belonging to an organization.

        Args:
            organization_id: Organization whose professors to return.

        Returns:
            Professors ordered by name.
        """
        return await self._professors.get_by_organization(organization_id)

    async def list_accepting_students(self) -> list[Professor]:
        """Return professors currently flagged as accepting students.

        Returns:
            Professors whose ``is_accepting_students`` is ``True``.
        """
        return await self._professors.list_accepting_students()

    async def _require_organization(self, organization_id: int) -> None:
        """Raise if the referenced organization does not exist."""
        if await self._organizations.get_by_id(organization_id) is None:
            raise ValidationError(f"Organization {organization_id} does not exist")
