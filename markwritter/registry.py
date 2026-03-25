"""Skill registry for managing available skills."""

import logging
from pathlib import Path
from typing import Optional

from markwritter.models import SkillDefinition

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for loading and managing skills."""

    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir
        self._skills: dict[str, SkillDefinition] = {}
        self._load_skills()

    def _load_skills(self) -> None:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            return

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            yaml_path = skill_dir / "skill.yaml"
            if yaml_path.exists():
                try:
                    skill_def = SkillDefinition.from_yaml(yaml_path)
                    self._skills[skill_def.name] = skill_def
                except Exception as e:
                    logger.warning("Failed to load skill from %s: %s", skill_dir, e)

    def get(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill definition by name."""
        return self._skills.get(name)

    def list_all(self) -> list[SkillDefinition]:
        """List all loaded skills."""
        return list(self._skills.values())

    def reload(self) -> None:
        """Reload all skills from disk."""
        self._skills.clear()
        self._load_skills()
