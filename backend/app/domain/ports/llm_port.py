from typing import Protocol

from app.domain.entities.opportunity import Opportunity
from app.domain.entities.user_profile import UserProfile


class MatchResult:
    """Structured output from the LLM match scorer."""

    def __init__(self, score: int, rationale: str) -> None:
        if not 0 <= score <= 100:
            raise ValueError(f"Match score must be 0-100, got {score}")
        self.score = score
        self.rationale = rationale


class LLMPort(Protocol):
    """
    Provider-agnostic interface for LLM operations.

    Implementations live in infrastructure/llm/ (one per provider).
    All calls are async and cached by content hash to avoid redundant API calls.
    """

    async def summarize(self, opportunity: Opportunity) -> str:
        """Generate a concise 2-3 sentence summary of the opportunity."""
        ...

    async def score_match(
        self,
        opportunity: Opportunity,
        profile: UserProfile,
    ) -> MatchResult:
        """Score how well an opportunity matches a user's profile (0-100)."""
        ...

    async def extract_skills(self, text: str) -> list[str]:
        """Extract a list of skills/technologies mentioned in the text."""
        ...

    async def generate_email_draft(
        self,
        opportunity: Opportunity,
        profile: UserProfile,
        professor_name: str = "",
    ) -> str:
        """Draft a cold email for the opportunity. Used by EmailDraftAgent."""
        ...
