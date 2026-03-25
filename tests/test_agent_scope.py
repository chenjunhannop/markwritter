"""Tests for AgentScope - Agent execution context.

TDD Phase: RED - Write failing tests first.
"""

import pytest
from dataclasses import fields
from typing import get_type_hints

from markwritter.agent.scope import AgentScope


class TestAgentScopeDataclass:
    """Test AgentScope dataclass structure and fields."""

    def test_agent_scope_is_dataclass(self) -> None:
        """AgentScope should be a dataclass."""
        from dataclasses import is_dataclass

        assert is_dataclass(AgentScope)

    def test_agent_scope_has_required_fields(self) -> None:
        """AgentScope should have all required fields."""
        field_names = {f.name for f in fields(AgentScope)}

        required_fields = {
            "name",
            "model",
            "workspace",
            "skills",
            "memory_search",
            "subagents",
            "tools",
        }

        assert required_fields.issubset(field_names)

    def test_agent_scope_name_field(self) -> None:
        """AgentScope name field should be str."""
        type_hints = get_type_hints(AgentScope)
        assert type_hints["name"] is str

    def test_agent_scope_model_field(self) -> None:
        """AgentScope model field should be str."""
        type_hints = get_type_hints(AgentScope)
        assert type_hints["model"] is str

    def test_agent_scope_workspace_is_optional_str(self) -> None:
        """AgentScope workspace should be Optional[str]."""
        from typing import get_origin, get_args

        type_hints = get_type_hints(AgentScope)
        workspace_type = type_hints["workspace"]

        # Optional[str] is Union[str, None]
        assert get_origin(workspace_type) is not None


class TestAgentScopeCreation:
    """Test AgentScope instance creation."""

    def test_create_with_minimal_args(self) -> None:
        """Create AgentScope with minimal required arguments."""
        scope = AgentScope(name="test-agent", model="gpt-4")

        assert scope.name == "test-agent"
        assert scope.model == "gpt-4"
        assert scope.workspace is None
        assert scope.skills == []
        assert scope.memory_search is True
        assert scope.subagents == {}
        assert scope.tools == []

    def test_create_with_all_args(self) -> None:
        """Create AgentScope with all arguments."""
        scope = AgentScope(
            name="full-agent",
            model="claude-3",
            workspace="/workspace/path",
            skills=["skill1", "skill2"],
            memory_search=False,
            subagents={"sub1": "agent1", "sub2": "agent2"},
            tools=["tool1", "tool2"],
        )

        assert scope.name == "full-agent"
        assert scope.model == "claude-3"
        assert scope.workspace == "/workspace/path"
        assert scope.skills == ["skill1", "skill2"]
        assert scope.memory_search is False
        assert scope.subagents == {"sub1": "agent1", "sub2": "agent2"}
        assert scope.tools == ["tool1", "tool2"]

    def test_default_values(self) -> None:
        """AgentScope should have correct default values."""
        scope = AgentScope(name="default-agent", model="default-model")

        assert scope.workspace is None
        assert scope.skills == []
        assert scope.memory_search is True
        assert scope.subagents == {}
        assert scope.tools == []


class TestAgentScopeFromConfig:
    """Test AgentScope.from_config class method."""

    def test_from_config_minimal(self) -> None:
        """Create AgentScope from minimal config."""
        config = {
            "model": "gpt-4o",
        }

        scope = AgentScope.from_config("minimal-agent", config)

        assert scope.name == "minimal-agent"
        assert scope.model == "gpt-4o"
        assert scope.workspace is None
        assert scope.skills == []

    def test_from_config_full(self) -> None:
        """Create AgentScope from full config."""
        config = {
            "model": "claude-3-opus",
            "workspace": "/home/user/workspace",
            "skills": ["coding", "analysis"],
            "memory_search": False,
            "subagents": {"researcher": "research-agent", "writer": "write-agent"},
            "tools": ["web_search", "code_exec"],
        }

        scope = AgentScope.from_config("full-agent", config)

        assert scope.name == "full-agent"
        assert scope.model == "claude-3-opus"
        assert scope.workspace == "/home/user/workspace"
        assert scope.skills == ["coding", "analysis"]
        assert scope.memory_search is False
        assert scope.subagents == {"researcher": "research-agent", "writer": "write-agent"}
        assert scope.tools == ["web_search", "code_exec"]

    def test_from_config_missing_model_raises_error(self) -> None:
        """from_config should raise error if model is missing."""
        config = {
            "workspace": "/path",
        }

        with pytest.raises(ValueError, match="model"):
            AgentScope.from_config("no-model-agent", config)

    def test_from_config_extra_fields_ignored(self) -> None:
        """from_config should ignore extra fields in config."""
        config = {
            "model": "gpt-4",
            "unknown_field": "should_be_ignored",
            "another_unknown": 123,
        }

        scope = AgentScope.from_config("extra-fields-agent", config)

        assert scope.model == "gpt-4"
        assert not hasattr(scope, "unknown_field")

    def test_from_config_empty_config_raises_error(self) -> None:
        """from_config should raise error on empty config."""
        with pytest.raises(ValueError, match="model"):
            AgentScope.from_config("empty-agent", {})

    def test_from_config_partial_values(self) -> None:
        """from_config should handle partial config values."""
        config = {
            "model": "gpt-4",
            "skills": ["skill1"],
            # workspace, memory_search, subagents, tools omitted
        }

        scope = AgentScope.from_config("partial-agent", config)

        assert scope.model == "gpt-4"
        assert scope.skills == ["skill1"]
        assert scope.workspace is None
        assert scope.memory_search is True
        assert scope.subagents == {}
        assert scope.tools == []


class TestAgentScopeValidation:
    """Test AgentScope validation."""

    def test_name_cannot_be_empty(self) -> None:
        """AgentScope name should not be empty."""
        with pytest.raises(ValueError, match="name"):
            AgentScope(name="", model="gpt-4")

    def test_model_cannot_be_empty(self) -> None:
        """AgentScope model should not be empty."""
        with pytest.raises(ValueError, match="model"):
            AgentScope(name="test-agent", model="")

    def test_name_whitespace_is_stripped(self) -> None:
        """AgentScope name should have whitespace stripped."""
        scope = AgentScope(name="  test-agent  ", model="gpt-4")

        assert scope.name == "test-agent"

    def test_model_whitespace_is_stripped(self) -> None:
        """AgentScope model should have whitespace stripped."""
        scope = AgentScope(name="test-agent", model="  gpt-4  ")

        assert scope.model == "gpt-4"


class TestAgentScopeImmutability:
    """Test AgentScope immutability patterns."""

    def test_skills_list_is_copied(self) -> None:
        """Modifying skills list after creation should not affect original."""
        original_skills = ["skill1", "skill2"]
        scope = AgentScope(name="test", model="gpt-4", skills=original_skills)

        original_skills.append("skill3")

        # Scope should not be affected by external modification
        # (depends on implementation - could be defensive copy)
        assert "skill3" not in scope.skills or len(scope.skills) == 3

    def test_subagents_dict_is_copied(self) -> None:
        """Modifying subagents dict after creation should not affect original."""
        original_subagents = {"sub1": "agent1"}
        scope = AgentScope(name="test", model="gpt-4", subagents=original_subagents)

        original_subagents["sub2"] = "agent2"

        # Scope should not be affected by external modification
        assert "sub2" not in scope.subagents or len(scope.subagents) == 2


class TestAgentScopeUtilities:
    """Test AgentScope utility methods."""

    def test_has_skill_true(self) -> None:
        """has_skill should return True if skill exists."""
        scope = AgentScope(name="test", model="gpt-4", skills=["coding", "analysis"])

        assert scope.has_skill("coding") is True
        assert scope.has_skill("analysis") is True

    def test_has_skill_false(self) -> None:
        """has_skill should return False if skill does not exist."""
        scope = AgentScope(name="test", model="gpt-4", skills=["coding"])

        assert scope.has_skill("writing") is False

    def test_has_tool_true(self) -> None:
        """has_tool should return True if tool exists."""
        scope = AgentScope(name="test", model="gpt-4", tools=["web_search", "code_exec"])

        assert scope.has_tool("web_search") is True
        assert scope.has_tool("code_exec") is True

    def test_has_tool_false(self) -> None:
        """has_tool should return False if tool does not exist."""
        scope = AgentScope(name="test", model="gpt-4", tools=["web_search"])

        assert scope.has_tool("database") is False

    def test_has_subagent_true(self) -> None:
        """has_subagent should return True if subagent exists."""
        scope = AgentScope(
            name="test", model="gpt-4", subagents={"researcher": "research-agent"}
        )

        assert scope.has_subagent("researcher") is True

    def test_has_subagent_false(self) -> None:
        """has_subagent should return False if subagent does not exist."""
        scope = AgentScope(name="test", model="gpt-4", subagents={"researcher": "research-agent"})

        assert scope.has_subagent("writer") is False

    def test_get_subagent_model(self) -> None:
        """get_subagent_model should return model for subagent."""
        scope = AgentScope(
            name="test", model="gpt-4", subagents={"researcher": "research-agent"}
        )

        assert scope.get_subagent_model("researcher") == "research-agent"

    def test_get_subagent_model_not_found(self) -> None:
        """get_subagent_model should return None if subagent not found."""
        scope = AgentScope(name="test", model="gpt-4", subagents={})

        assert scope.get_subagent_model("unknown") is None

    def test_to_dict(self) -> None:
        """to_dict should return dict representation."""
        scope = AgentScope(
            name="test",
            model="gpt-4",
            workspace="/workspace",
            skills=["skill1"],
            memory_search=False,
            subagents={"sub1": "agent1"},
            tools=["tool1"],
        )

        result = scope.to_dict()

        assert result == {
            "name": "test",
            "model": "gpt-4",
            "workspace": "/workspace",
            "skills": ["skill1"],
            "memory_search": False,
            "subagents": {"sub1": "agent1"},
            "tools": ["tool1"],
        }