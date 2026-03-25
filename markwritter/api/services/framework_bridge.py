"""Framework bridge service - connects API layer to core Framework."""

from pathlib import Path
from typing import Optional

from markwritter.core import Framework
from markwritter.registry import SkillRegistry

_framework_instance: Optional[Framework] = None


def get_framework() -> Framework:
    """Get or create Framework singleton instance."""
    global _framework_instance
    if _framework_instance is None:
        skills_dir = Path("./skills").resolve()
        registry = SkillRegistry(skills_dir)
        _framework_instance = Framework(registry)
    return _framework_instance


def reset_framework() -> None:
    """Reset framework instance (mainly for testing)."""
    global _framework_instance
    _framework_instance = None
