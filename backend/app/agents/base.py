"""
Agent interface — scaffolded for future autonomous agents.

An Agent is an LLM reasoning loop that:
  1. Receives a goal (natural-language string).
  2. Selects and calls Tools from the registry to gather information or act.
  3. Iterates until the goal is satisfied or a step limit is reached.

Planned agents (not yet implemented):
  - SourceDiscoveryAgent  — finds new internship/job sources automatically
  - DeadlineMonitorAgent  — tracks and alerts on application deadlines
  - RankingAgent          — re-ranks opportunities based on updated profile
  - ReminderAgent         — sends personalised application reminders
  - ProfessorSuggester    — recommends professors to contact
  - EmailDraftAgent       — generates cold email drafts

Adding an agent:
  1. Create app/agents/<name>.py implementing the Agent protocol below.
  2. Register it in app/agents/registry.py.
  3. Expose it via a Celery task in app/workers/tasks/agents.py.
"""

from typing import Any, Protocol, runtime_checkable

from app.tools.base import Tool


@runtime_checkable
class Agent(Protocol):
    """Minimal interface every autonomous agent must satisfy."""

    name: str
    description: str
    tools: list[Tool]

    async def run(self, goal: str, **kwargs: Any) -> Any:
        """Execute the agent loop toward the given goal."""
        ...
