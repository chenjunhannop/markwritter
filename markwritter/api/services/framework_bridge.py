"""Framework bridge service - connects API layer to core Framework.

This module provides a singleton pattern for accessing the Framework instance
from the API layer. It serves as a bridge between the web API and the core
skill execution framework.

Purpose:
    - Provides global access to Framework instance for API routes
    - Manages Framework lifecycle (creation and reset)
    - Decouples API layer from Framework initialization details

Usage:
    from markwritter.api.services.framework_bridge import get_framework

    # Get Framework instance (creates on first call)
    framework = get_framework()

    # Access skills registry
    skills = framework.registry.list_all()

    # Execute a skill
    result = framework.run_skill("skill-name", {"param": "value"})

    # Reset for testing
    reset_framework()

Note:
    This is a transitional module. In a future refactoring, we should
    consider using dependency injection instead of global state for
    better testability and explicit dependencies.
"""

from pathlib import Path
from typing import Optional

from markwritter.core import Framework
from markwritter.registry import SkillRegistry

_framework_instance: Optional[Framework] = None


def get_framework() -> Framework:
    """Get or create Framework singleton instance.

    Creates a new Framework instance on first call with default
    configuration (skills from ./skills directory). Subsequent
    calls return the same instance.

    Returns:
        Framework: The global Framework instance

    Example:
        >>> framework = get_framework()
        >>> skills = framework.registry.list_all()
    """
    global _framework_instance
    if _framework_instance is None:
        skills_dir = Path("./skills").resolve()
        registry = SkillRegistry(skills_dir)
        _framework_instance = Framework(registry)
    return _framework_instance


def reset_framework() -> None:
    """Reset framework instance.

    Clears the singleton instance, causing the next get_framework()
    call to create a new Framework. Use this for:

    - Testing: Reset between test cases
    - Hot-reload: Reload skills after configuration changes

    Example:
        >>> reset_framework()
        >>> framework = get_framework()  # Creates new instance
    """
    global _framework_instance
    _framework_instance = None
