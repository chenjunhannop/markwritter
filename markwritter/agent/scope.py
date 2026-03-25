"""Agent execution context.

AgentScope defines the execution context for an agent, including:
- Model selection
- Available skills and tools
- Subagent configuration
- Memory search settings
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentScope:
    """Agent execution context.

    Defines the configuration and capabilities of an agent.

    Attributes:
        name: Unique identifier for the agent
        model: LLM model to use (e.g., "gpt-4", "claude-3-opus")
        workspace: Optional working directory path
        skills: List of skill names available to the agent
        memory_search: Whether to enable memory search
        subagents: Mapping of subagent name to model
        tools: List of tool names available to the agent

    Example:
        >>> scope = AgentScope(
        ...     name="research-agent",
        ...     model="gpt-4",
        ...     skills=["web_search", "summarize"],
        ...     memory_search=True
        ... )
        >>> scope.has_skill("web_search")
        True
    """

    name: str
    model: str
    workspace: Optional[str] = None
    skills: list[str] = field(default_factory=list)
    memory_search: bool = True
    subagents: dict[str, str] = field(default_factory=dict)
    tools: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and normalize fields after initialization."""
        # Strip whitespace
        self.name = self.name.strip()
        self.model = self.model.strip()

        # Validate required fields
        if not self.name:
            raise ValueError("Agent name cannot be empty")
        if not self.model:
            raise ValueError("Agent model cannot be empty")

        # Defensive copy of mutable fields
        self.skills = list(self.skills)
        self.subagents = dict(self.subagents)
        self.tools = list(self.tools)

    @classmethod
    def from_config(cls, name: str, config: dict[str, Any]) -> "AgentScope":
        """Create AgentScope from configuration dict.

        Args:
            name: Agent name
            config: Configuration dictionary

        Returns:
            AgentScope instance

        Raises:
            ValueError: If required field 'model' is missing

        Example:
            >>> config = {"model": "gpt-4", "skills": ["coding"]}
            >>> scope = AgentScope.from_config("my-agent", config)
            >>> scope.model
            'gpt-4'
        """
        if "model" not in config:
            raise ValueError(f"Agent '{name}' config missing required field: model")

        return cls(
            name=name,
            model=config["model"],
            workspace=config.get("workspace"),
            skills=config.get("skills", []),
            memory_search=config.get("memory_search", True),
            subagents=config.get("subagents", {}),
            tools=config.get("tools", []),
        )

    def has_skill(self, skill_name: str) -> bool:
        """Check if agent has a specific skill.

        Args:
            skill_name: Name of the skill to check

        Returns:
            True if skill is available
        """
        return skill_name in self.skills

    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has a specific tool.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is available
        """
        return tool_name in self.tools

    def has_subagent(self, subagent_name: str) -> bool:
        """Check if agent has a specific subagent.

        Args:
            subagent_name: Name of the subagent to check

        Returns:
            True if subagent is configured
        """
        return subagent_name in self.subagents

    def get_subagent_model(self, subagent_name: str) -> Optional[str]:
        """Get the model for a subagent.

        Args:
            subagent_name: Name of the subagent

        Returns:
            Model name or None if subagent not found
        """
        return self.subagents.get(subagent_name)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all fields
        """
        return {
            "name": self.name,
            "model": self.model,
            "workspace": self.workspace,
            "skills": list(self.skills),
            "memory_search": self.memory_search,
            "subagents": dict(self.subagents),
            "tools": list(self.tools),
        }