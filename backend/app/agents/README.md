# Agents

This module is scaffolded for future autonomous AI agents. No agents are implemented in the MVP.

## What is an Agent here?

An Agent is an LLM reasoning loop that:
1. Receives a goal in natural language.
2. Selects and calls **Tools** from `app/tools/` to gather information or act.
3. Iterates until the goal is satisfied or a step limit is reached.

## Planned Agents

| Agent | Goal |
|---|---|
| `SourceDiscoveryAgent` | Discover new internship/job sources automatically |
| `DeadlineMonitorAgent` | Track application deadlines and alert before they pass |
| `RankingAgent` | Re-rank opportunities when the user profile is updated |
| `ReminderAgent` | Send personalised application reminders |
| `ProfessorSuggesterAgent` | Recommend professors to contact based on research interests |
| `EmailDraftAgent` | Generate cold email drafts for specific opportunities |

## How to Add an Agent

1. Create `app/agents/<name>.py` implementing the `Agent` protocol in `base.py`.
2. List the tools it needs from `app/tools/`.
3. Register it in `app/agents/registry.py` (to be created).
4. Expose it via a Celery task in `app/workers/tasks/agents.py` (to be created).

## Why Tools are the Key Abstraction

The same service methods used by the deterministic pipeline (scrape, score, notify, query)
are wrapped as Tools so agents can call them without knowing about the pipeline.
This means adding an agent never requires refactoring existing code.
