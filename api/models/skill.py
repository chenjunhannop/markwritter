"""Skill API models."""

from typing import Any

from pydantic import BaseModel

from markwritter.models import SkillDefinition


class SkillResponse(BaseModel):
    """Response model for skill."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    inputs: list[dict[str, Any]] = []
    output: dict[str, str] = {}

    @classmethod
    def from_definition(cls, skill: SkillDefinition) -> "SkillResponse":
        """Create response from SkillDefinition."""
        return cls(
            name=skill.name,
            description=skill.description,
            version=skill.version,
            inputs=[i.model_dump() for i in skill.inputs],
            output=skill.output.model_dump(),
        )


class SkillRunRequest(BaseModel):
    """Request model for running a skill."""

    params: dict[str, Any] = {}


class SkillRunResponse(BaseModel):
    """Response model for skill execution."""

    success: bool
    output: str = ""
    error: str = ""
