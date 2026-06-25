from dataclasses import dataclass
from datetime import datetime


@dataclass
class OpportunityMatch:
    """
    The result of scoring an Opportunity against a UserProfile.

    `match_score` is 0-100 (LLM + structured pre-filter combined).
    `match_rationale` is the LLM's explanation — shown in the dashboard and
    used by the RankingAgent when re-ordering after profile updates.

    The `is_applied` / `applied_at` fields let the user track their applications
    without needing a separate app-tracking tool.
    """

    profile_id: int
    opportunity_id: int
    match_score: int                # 0-100

    id: int | None = None
    match_rationale: str = ""       # AI-generated explanation
    is_saved: bool = False
    is_applied: bool = False
    applied_at: datetime | None = None
    application_notes: str = ""
    is_notified: bool = False       # has an email been sent for this match?
    notified_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_strong_match(self) -> bool:
        return self.match_score >= 80

    @property
    def is_good_match(self) -> bool:
        return self.match_score >= 60
