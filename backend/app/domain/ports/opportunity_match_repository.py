from typing import Protocol

from app.domain.entities.opportunity_match import OpportunityMatch


class OpportunityMatchRepository(Protocol):
    async def get_by_id(self, id: int) -> OpportunityMatch | None: ...
    async def get_by_profile_and_opportunity(
        self, profile_id: int, opportunity_id: int
    ) -> OpportunityMatch | None: ...
    async def save(self, match: OpportunityMatch) -> OpportunityMatch: ...
    async def update(self, match: OpportunityMatch) -> OpportunityMatch: ...
    async def list_by_profile(
        self,
        profile_id: int,
        min_score: int = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> list[OpportunityMatch]: ...
    async def list_unnotified_above_threshold(
        self, profile_id: int, min_score: int
    ) -> list[OpportunityMatch]: ...
