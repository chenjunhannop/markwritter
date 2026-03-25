"""Model Router for routing files to appropriate LLM models.

This module provides functionality to route files to different LLM models
based on configurable routing rules using glob patterns and task type filters.
"""

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Optional


@dataclass
class RoutingRule:
    """Routing rule for matching files to models.

    Attributes:
        pattern: Glob pattern for matching file paths (e.g., "**/drafts/*")
        model: Model identifier in provider/model format (e.g., "openai/gpt-4")
        task_types: Optional tuple of task types this rule applies to.
                   Empty tuple means the rule applies to all task types.
    """

    pattern: str
    model: str
    task_types: tuple[str, ...] = ()

    def matches(self, file_path: str, task_type: Optional[str]) -> bool:
        """Check if this rule matches the given file path and task type.

        Args:
            file_path: The file path to match against.
            task_type: Optional task type for filtering.

        Returns:
            True if the rule matches, False otherwise.
        """
        # Normalize path separators for consistent matching
        normalized_path = file_path.replace("\\", "/")

        # Check pattern match
        if not self._match_pattern(normalized_path):
            return False

        # If rule has no task type filter, it matches any task type
        if not self.task_types:
            return True

        # If rule has task type filter but no task type provided, no match
        if task_type is None:
            return False

        # Check if task type matches
        return task_type in self.task_types

    def _match_pattern(self, path: str) -> bool:
        """Match path against the glob pattern.

        Args:
            path: Normalized path with forward slashes.

        Returns:
            True if pattern matches, False otherwise.
        """
        # Handle empty or whitespace-only paths
        if not path or not path.strip():
            return False

        # Strip trailing slashes for consistent matching
        path = path.rstrip("/")

        # Handle trailing empty pattern components (e.g., **/drafts/)
        pattern = self.pattern.rstrip("/")

        # Use fnmatch for glob pattern matching
        # fnmatch treats ** as literal characters, so we need special handling
        if "**" in pattern:
            return self._match_globstar(path)
        else:
            # For patterns without **, ensure * doesn't match path separators
            return self._match_simple_glob(path, pattern)

    def _match_simple_glob(self, path: str, pattern: str) -> bool:
        """Match path against simple glob pattern (no **).

        In standard glob semantics, * does NOT match path separators.
        However, fnmatch's * DOES match /. We need to handle this.

        Args:
            path: Normalized path with forward slashes.
            pattern: Glob pattern without **.

        Returns:
            True if pattern matches, False otherwise.
        """
        # If pattern contains /, split and match component-wise
        if "/" in pattern or "/" in path:
            pattern_parts = pattern.split("/")
            path_parts = path.split("/")

            # Pattern must have same number of components as path
            if len(pattern_parts) != len(path_parts):
                return False

            # Match each component
            for pp, fp in zip(pattern_parts, path_parts):
                if not fnmatch(fp, pp):
                    return False
            return True
        else:
            # Simple filename match
            return fnmatch(path, pattern)

    def _match_globstar(self, path: str) -> bool:
        """Handle glob pattern with ** (globstar).

        Args:
            path: Normalized path with forward slashes (already stripped trailing slash).

        Returns:
            True if pattern matches, False otherwise.
        """
        # Convert glob pattern to regex-like matching
        # ** matches zero or more directories
        pattern_parts = self.pattern.rstrip("/").split("/")
        path_parts = path.split("/")

        # Handle absolute paths (leading empty string after split)
        # e.g., "/test/file.md" -> ["", "test", "file.md"]
        # Pattern "**/test/*" should match
        if path_parts and path_parts[0] == "":
            path_parts = path_parts[1:]  # Remove leading empty string

        # Handle patterns starting with /
        if pattern_parts and pattern_parts[0] == "":
            pattern_parts = pattern_parts[1:]

        return self._match_parts(pattern_parts, path_parts, 0, 0)

    def _match_parts(
        self, pattern_parts: list[str], path_parts: list[str], pi: int, ppi: int
    ) -> bool:
        """Recursively match pattern parts against path parts.

        Args:
            pattern_parts: Split pattern components.
            path_parts: Split path components.
            pi: Current pattern index.
            ppi: Current path index.

        Returns:
            True if remaining parts match.
        """
        # Both exhausted - match
        if pi >= len(pattern_parts) and ppi >= len(path_parts):
            return True

        # Pattern exhausted but path remains - no match
        if pi >= len(pattern_parts):
            return False

        # Path exhausted but pattern remains - only match if remaining pattern is **
        if ppi >= len(path_parts):
            return all(p == "**" for p in pattern_parts[pi:])

        current_pattern = pattern_parts[pi]

        if current_pattern == "**":
            # ** can match zero or more path components
            # Try matching zero components (skip **)
            if self._match_parts(pattern_parts, path_parts, pi + 1, ppi):
                return True
            # Try matching one or more components
            if self._match_parts(pattern_parts, path_parts, pi, ppi + 1):
                return True
            return False
        else:
            # Regular pattern component - use fnmatch for wildcards
            if fnmatch(path_parts[ppi], current_pattern):
                return self._match_parts(pattern_parts, path_parts, pi + 1, ppi + 1)
            return False


class ModelRouter:
    """Router for selecting LLM models based on file paths and task types.

    The router evaluates rules in order and returns the model from the first
    matching rule. If no rule matches, the default model is returned.
    """

    def __init__(self, rules: list[RoutingRule], default_model: str):
        """Initialize the model router.

        Args:
            rules: List of routing rules to evaluate in order.
            default_model: Default model to use when no rule matches.
        """
        self.rules = rules
        self.default_model = default_model

    def get_model(self, file_path: str, task_type: Optional[str] = None) -> str:
        """Get the model for a given file path and optional task type.

        Args:
            file_path: The file path to route.
            task_type: Optional task type for filtering.

        Returns:
            The model identifier (either from matching rule or default).
        """
        for rule in self.rules:
            if rule.matches(file_path, task_type):
                return rule.model

        return self.default_model

    @classmethod
    def from_config(cls, config: dict, default_model: str) -> "ModelRouter":
        """Create a ModelRouter from a configuration dictionary.

        Args:
            config: Configuration dictionary with optional "rules" key.
                    Each rule should have "pattern", "model", and optional "task_types".
            default_model: Default model to use when no rule matches.

        Returns:
            Configured ModelRouter instance.
        """
        rules_data = config.get("rules") or []
        rules = []

        for rule_config in rules_data:
            if not isinstance(rule_config, dict):
                continue

            pattern = rule_config.get("pattern", "")
            model = rule_config.get("model", "")
            task_types = tuple(rule_config.get("task_types", []))

            if pattern and model:
                rules.append(
                    RoutingRule(
                        pattern=pattern,
                        model=model,
                        task_types=task_types,
                    )
                )

        return cls(rules=rules, default_model=default_model)
