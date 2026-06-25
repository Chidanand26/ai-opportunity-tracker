"""
Tool interface — the seam between application services and AI agents.

Every capability that an autonomous agent might need (search opportunities,
score matches, send email, discover sources) is wrapped as a Tool.
Agents compose tools into goal-directed loops; the pipeline calls the same
underlying service methods directly.

This module defines the protocol that all tools must implement.
"""

from typing import Any, ClassVar, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """Minimal interface every tool must satisfy."""

    name: str
    description: str

    async def run(self, **kwargs: Any) -> Any:
        """Execute the tool with the given keyword arguments."""
        ...


class ToolRegistry:
    """
    Singleton registry of available tools.

    Agents discover capabilities by inspecting registered tools.
    Each tool's name and description form part of the agent's system prompt.
    """

    _tools: ClassVar[dict[str, Tool]] = {}

    @classmethod
    def register(cls, tool: Tool) -> Tool:
        """Register a tool. Use as a decorator: @ToolRegistry.register."""
        cls._tools[tool.name] = tool
        return tool

    @classmethod
    def get(cls, name: str) -> Tool:
        if name not in cls._tools:
            raise KeyError(f"Tool '{name}' not found. Available: {list(cls._tools)}")
        return cls._tools[name]

    @classmethod
    def all(cls) -> list[Tool]:
        return list(cls._tools.values())
