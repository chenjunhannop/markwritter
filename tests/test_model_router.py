"""Tests for ModelRouter.

TDD approach: Tests for model routing before implementation.
"""

from unittest.mock import patch

import pytest

from markwritter.model_router import ModelRouter, RoutingRule


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def basic_rules() -> list[RoutingRule]:
    """Create basic routing rules for testing."""
    return [
        RoutingRule(pattern="**/drafts/*", model="openai/gpt-4"),
        RoutingRule(pattern="**/*.md", model="anthropic/claude-3"),
        RoutingRule(pattern="**/daily/**", model="qwen/qwen3.5-plus"),
    ]


@pytest.fixture
def rules_with_task_types() -> list[RoutingRule]:
    """Create routing rules with task type filtering."""
    return [
        RoutingRule(
            pattern="**/drafts/*",
            model="openai/gpt-4",
            task_types=("summarize", "rewrite"),
        ),
        RoutingRule(
            pattern="**/*.md",
            model="anthropic/claude-3",
            task_types=("translate",),
        ),
        RoutingRule(pattern="**/daily/**", model="qwen/qwen3.5-plus"),
    ]


@pytest.fixture
def default_model() -> str:
    """Default model for testing."""
    return "qwen/qwen3.5-plus"


# ==============================================================================
# RoutingRule Tests
# ==============================================================================


class TestRoutingRuleInit:
    """Tests for RoutingRule initialization."""

    def test_init_with_required_fields(self) -> None:
        """Test initialization with only required fields."""
        rule = RoutingRule(pattern="**/drafts/*", model="openai/gpt-4")
        assert rule.pattern == "**/drafts/*"
        assert rule.model == "openai/gpt-4"
        assert rule.task_types == ()

    def test_init_with_task_types(self) -> None:
        """Test initialization with task types."""
        rule = RoutingRule(
            pattern="**/drafts/*",
            model="openai/gpt-4",
            task_types=("summarize", "rewrite"),
        )
        assert rule.task_types == ("summarize", "rewrite")

    def test_init_with_empty_task_types(self) -> None:
        """Test initialization with empty task types."""
        rule = RoutingRule(
            pattern="**/drafts/*",
            model="openai/gpt-4",
            task_types=(),
        )
        assert rule.task_types == ()


class TestRoutingRuleMatches:
    """Tests for RoutingRule.matches method."""

    def test_matches_simple_pattern(self) -> None:
        """Test matching with simple glob pattern.

        Standard glob semantics:
        - ** matches zero or more directories
        - * matches single path component (does not cross directory boundaries)
        - **/drafts/* matches files directly in drafts/ but not in subdirectories
        - **/drafts/** matches files at any level under drafts/
        """
        rule = RoutingRule(pattern="**/drafts/*", model="openai/gpt-4")
        assert rule.matches("/Users/test/drafts/note.md", None) is True
        # * does not cross directories - use ** for that
        assert rule.matches("/Users/test/drafts/ideas/draft.md", None) is False
        assert rule.matches("/Users/test/notes/note.md", None) is False

    def test_matches_simple_pattern_with_globstar(self) -> None:
        """Test matching with globstar to match files in subdirectories."""
        rule = RoutingRule(pattern="**/drafts/**", model="openai/gpt-4")
        assert rule.matches("/Users/test/drafts/note.md", None) is True
        assert rule.matches("/Users/test/drafts/ideas/draft.md", None) is True
        assert rule.matches("/Users/test/drafts/ideas/notes/file.md", None) is True
        assert rule.matches("/Users/test/notes/note.md", None) is False

    def test_matches_with_file_extension(self) -> None:
        """Test matching with file extension pattern."""
        rule = RoutingRule(pattern="**/*.md", model="anthropic/claude-3")
        assert rule.matches("/Users/test/notes/note.md", None) is True
        assert rule.matches("/Users/test/note.txt", None) is False
        assert rule.matches("/path/to/file.md", None) is True

    def test_matches_with_directory_pattern(self) -> None:
        """Test matching with directory pattern."""
        rule = RoutingRule(pattern="**/daily/**", model="qwen/qwen3.5-plus")
        assert rule.matches("/Users/test/daily/2024-01-15.md", None) is True
        assert rule.matches("/path/to/daily/notes/note.md", None) is True
        assert rule.matches("/Users/test/notes/2024-01-15.md", None) is False

    def test_matches_with_task_type_filter_matching(self) -> None:
        """Test matching when task type filter matches."""
        rule = RoutingRule(
            pattern="**/*.md",
            model="openai/gpt-4",
            task_types=("summarize", "rewrite"),
        )
        assert rule.matches("/test/note.md", "summarize") is True
        assert rule.matches("/test/note.md", "rewrite") is True

    def test_matches_with_task_type_filter_not_matching(self) -> None:
        """Test matching when task type filter does not match."""
        rule = RoutingRule(
            pattern="**/*.md",
            model="openai/gpt-4",
            task_types=("summarize", "rewrite"),
        )
        assert rule.matches("/test/note.md", "translate") is False
        assert rule.matches("/test/note.md", "classify") is False

    def test_matches_with_task_type_filter_but_pattern_not_matching(self) -> None:
        """Test matching when task type matches but pattern does not."""
        rule = RoutingRule(
            pattern="**/drafts/*",
            model="openai/gpt-4",
            task_types=("summarize",),
        )
        assert rule.matches("/test/notes/note.md", "summarize") is False

    def test_matches_with_no_task_type_filter(self) -> None:
        """Test matching when no task type filter is specified."""
        rule = RoutingRule(pattern="**/*.md", model="openai/gpt-4")
        # Should match any task type when no filter is specified
        assert rule.matches("/test/note.md", None) is True
        assert rule.matches("/test/note.md", "summarize") is True
        assert rule.matches("/test/note.md", "translate") is True

    def test_matches_with_empty_task_type_and_filter(self) -> None:
        """Test matching when task type is None but rule has filter."""
        rule = RoutingRule(
            pattern="**/*.md",
            model="openai/gpt-4",
            task_types=("summarize",),
        )
        # When task_type is None but rule has task_types, it should NOT match
        assert rule.matches("/test/note.md", None) is False

    def test_matches_exact_filename(self) -> None:
        """Test matching with exact filename pattern."""
        rule = RoutingRule(pattern="**/README.md", model="openai/gpt-4")
        assert rule.matches("/project/README.md", None) is True
        assert rule.matches("/project/docs/README.md", None) is True
        assert rule.matches("/project/README.txt", None) is False

    def test_matches_single_asterisk(self) -> None:
        """Test matching with single asterisk pattern.

        Single asterisk (*) should NOT match path separators.
        This follows standard glob semantics.
        """
        rule = RoutingRule(pattern="*.md", model="openai/gpt-4")
        assert rule.matches("note.md", None) is True
        assert rule.matches("test.txt", None) is False
        # Single asterisk should NOT match path separators (standard glob)
        assert rule.matches("subdir/note.md", None) is False
        assert rule.matches("/absolute/note.md", None) is False

    def test_matches_complex_pattern(self) -> None:
        """Test matching with complex glob pattern."""
        rule = RoutingRule(pattern="**/drafts/**/*.md", model="openai/gpt-4")
        assert rule.matches("/test/drafts/note.md", None) is True
        assert rule.matches("/test/drafts/subdir/note.md", None) is True
        assert rule.matches("/test/drafts/file.txt", None) is False

    def test_matches_with_multiple_task_types(self) -> None:
        """Test matching with multiple task types in rule."""
        rule = RoutingRule(
            pattern="**/*.md",
            model="openai/gpt-4",
            task_types=("summarize", "rewrite", "translate"),
        )
        assert rule.matches("/test/note.md", "summarize") is True
        assert rule.matches("/test/note.md", "rewrite") is True
        assert rule.matches("/test/note.md", "translate") is True
        assert rule.matches("/test/note.md", "classify") is False


# ==============================================================================
# ModelRouter Initialization Tests
# ==============================================================================


class TestModelRouterInit:
    """Tests for ModelRouter initialization."""

    def test_init_with_rules_and_default(self, basic_rules: list[RoutingRule], default_model: str) -> None:
        """Test initialization with rules and default model."""
        router = ModelRouter(rules=basic_rules, default_model=default_model)
        assert router.rules == basic_rules
        assert router.default_model == default_model

    def test_init_with_empty_rules(self, default_model: str) -> None:
        """Test initialization with empty rules list."""
        router = ModelRouter(rules=[], default_model=default_model)
        assert router.rules == []
        assert router.default_model == default_model

    def test_init_preserves_rule_order(self, default_model: str) -> None:
        """Test that rule order is preserved."""
        rules = [
            RoutingRule(pattern="**/*.md", model="model-a"),
            RoutingRule(pattern="**/*.txt", model="model-b"),
            RoutingRule(pattern="**/*.rst", model="model-c"),
        ]
        router = ModelRouter(rules=rules, default_model=default_model)
        assert router.rules[0].model == "model-a"
        assert router.rules[1].model == "model-b"
        assert router.rules[2].model == "model-c"


# ==============================================================================
# ModelRouter get_model Tests
# ==============================================================================


class TestModelRouterGetModel:
    """Tests for ModelRouter.get_model method."""

    def test_get_model_matching_first_rule(self, basic_rules: list[RoutingRule], default_model: str) -> None:
        """Test getting model when first rule matches."""
        router = ModelRouter(rules=basic_rules, default_model=default_model)
        model = router.get_model("/Users/test/drafts/note.md")
        assert model == "openai/gpt-4"

    def test_get_model_matching_second_rule(self, basic_rules: list[RoutingRule], default_model: str) -> None:
        """Test getting model when second rule matches."""
        router = ModelRouter(rules=basic_rules, default_model=default_model)
        model = router.get_model("/Users/test/notes/readme.md")
        assert model == "anthropic/claude-3"

    def test_get_model_no_match_returns_default(self, basic_rules: list[RoutingRule], default_model: str) -> None:
        """Test returning default model when no rule matches."""
        router = ModelRouter(rules=basic_rules, default_model=default_model)
        model = router.get_model("/Users/test/notes/readme.txt")
        assert model == default_model

    def test_get_model_with_empty_rules_returns_default(self, default_model: str) -> None:
        """Test returning default model when no rules are configured."""
        router = ModelRouter(rules=[], default_model=default_model)
        model = router.get_model("/Users/test/any/path.md")
        assert model == default_model

    def test_get_model_with_task_type_filter(
        self, rules_with_task_types: list[RoutingRule], default_model: str
    ) -> None:
        """Test getting model with task type filtering."""
        router = ModelRouter(rules=rules_with_task_types, default_model=default_model)

        # Should match drafts pattern with summarize task
        model = router.get_model("/test/drafts/note.md", "summarize")
        assert model == "openai/gpt-4"

        # Should match .md pattern with translate task
        model = router.get_model("/test/notes/note.md", "translate")
        assert model == "anthropic/claude-3"

    def test_get_model_task_type_not_matching_rule(
        self, rules_with_task_types: list[RoutingRule], default_model: str
    ) -> None:
        """Test getting model when task type doesn't match first rule but matches another."""
        router = ModelRouter(rules=rules_with_task_types, default_model=default_model)

        # First rule (drafts) has task_types=(summarize, rewrite), translate doesn't match
        # Second rule (*.md) has task_types=(translate,), which matches
        model = router.get_model("/test/drafts/note.md", "translate")
        # Should match second rule since translate matches
        assert model == "anthropic/claude-3"

    def test_get_model_task_type_matches_no_rules(
        self, rules_with_task_types: list[RoutingRule], default_model: str
    ) -> None:
        """Test getting model when task type matches no rules."""
        router = ModelRouter(rules=rules_with_task_types, default_model=default_model)

        # "classify" task doesn't match any rule's task_types filter
        # The *.md rule only accepts translate, drafts rule only summarize/rewrite
        model = router.get_model("/test/drafts/note.md", "classify")
        assert model == default_model

    def test_get_model_rule_order_matters(self, default_model: str) -> None:
        """Test that first matching rule wins (rule order matters)."""
        rules = [
            RoutingRule(pattern="**/*.md", model="model-first"),
            RoutingRule(pattern="**/special/*.md", model="model-second"),
        ]
        router = ModelRouter(rules=rules, default_model=default_model)

        # First rule matches, so second rule is never evaluated
        model = router.get_model("/test/special/note.md")
        assert model == "model-first"

    def test_get_model_with_none_task_type(
        self, rules_with_task_types: list[RoutingRule], default_model: str
    ) -> None:
        """Test getting model with None task type."""
        router = ModelRouter(rules=rules_with_task_types, default_model=default_model)

        # Should match daily rule (no task type filter)
        model = router.get_model("/test/daily/2024-01-15.md", None)
        assert model == "qwen/qwen3.5-plus"

    def test_get_model_case_sensitive_pattern(self, default_model: str) -> None:
        """Test that pattern matching is case sensitive."""
        rules = [RoutingRule(pattern="**/*.MD", model="model-uppercase")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Glob matching is typically case-sensitive on Unix systems
        # But fnmatch behavior depends on the filesystem
        # We test the expected behavior of our implementation
        model = router.get_model("/test/note.md")
        # lowercase .md should not match uppercase .MD pattern
        assert model == default_model

    def test_get_model_with_special_characters_in_path(self, default_model: str) -> None:
        """Test matching with special characters in file path."""
        rules = [RoutingRule(pattern="**/drafts/*", model="openai/gpt-4")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Paths with spaces
        model = router.get_model("/test/drafts/my note.md")
        assert model == "openai/gpt-4"

        # Paths with unicode characters
        model = router.get_model("/test/drafts/\u4e2d\u6587\u7b14\u8bb0.md")
        assert model == "openai/gpt-4"


# ==============================================================================
# ModelRouter from_config Tests
# ==============================================================================


class TestModelRouterFromConfig:
    """Tests for ModelRouter.from_config class method."""

    def test_from_config_basic(self, default_model: str) -> None:
        """Test creating router from basic config."""
        config = {
            "rules": [
                {"pattern": "**/drafts/*", "model": "openai/gpt-4"},
                {"pattern": "**/*.md", "model": "anthropic/claude-3"},
            ]
        }
        router = ModelRouter.from_config(config, default_model)

        assert router.default_model == default_model
        assert len(router.rules) == 2
        assert router.rules[0].pattern == "**/drafts/*"
        assert router.rules[0].model == "openai/gpt-4"
        assert router.rules[1].pattern == "**/*.md"
        assert router.rules[1].model == "anthropic/claude-3"

    def test_from_config_with_task_types(self, default_model: str) -> None:
        """Test creating router from config with task types."""
        config = {
            "rules": [
                {
                    "pattern": "**/drafts/*",
                    "model": "openai/gpt-4",
                    "task_types": ["summarize", "rewrite"],
                }
            ]
        }
        router = ModelRouter.from_config(config, default_model)

        assert len(router.rules) == 1
        assert router.rules[0].task_types == ("summarize", "rewrite")

    def test_from_config_empty_rules(self, default_model: str) -> None:
        """Test creating router from config with empty rules."""
        config: dict[str, list] = {"rules": []}
        router = ModelRouter.from_config(config, default_model)

        assert router.rules == []
        assert router.default_model == default_model

    def test_from_config_missing_rules_key(self, default_model: str) -> None:
        """Test creating router from config without rules key."""
        config: dict = {}
        router = ModelRouter.from_config(config, default_model)

        assert router.rules == []
        assert router.default_model == default_model

    def test_from_config_with_none_rules(self, default_model: str) -> None:
        """Test creating router from config with None rules."""
        config: dict = {"rules": None}
        router = ModelRouter.from_config(config, default_model)

        assert router.rules == []
        assert router.default_model == default_model

    def test_from_config_preserves_rule_order(self, default_model: str) -> None:
        """Test that config rule order is preserved."""
        config = {
            "rules": [
                {"pattern": "**/*.md", "model": "model-a"},
                {"pattern": "**/*.txt", "model": "model-b"},
                {"pattern": "**/*.rst", "model": "model-c"},
            ]
        }
        router = ModelRouter.from_config(config, default_model)

        assert router.rules[0].model == "model-a"
        assert router.rules[1].model == "model-b"
        assert router.rules[2].model == "model-c"

    def test_from_config_complex_example(self, default_model: str) -> None:
        """Test creating router from a complex realistic config."""
        config = {
            "rules": [
                {
                    "pattern": "**/drafts/*",
                    "model": "openai/gpt-4",
                    "task_types": ["summarize", "rewrite"],
                },
                {
                    "pattern": "**/*.md",
                    "model": "anthropic/claude-3",
                    "task_types": ["translate"],
                },
                {
                    "pattern": "**/daily/**",
                    "model": "qwen/qwen3.5-plus",
                },
                {
                    "pattern": "**/technical/**",
                    "model": "deepseek/deepseek-coder",
                    "task_types": ["code", "explain"],
                },
            ]
        }
        router = ModelRouter.from_config(config, default_model)

        assert len(router.rules) == 4

        # Test routing behavior
        assert router.get_model("/test/drafts/note.md", "summarize") == "openai/gpt-4"
        assert router.get_model("/test/notes/readme.md", "translate") == "anthropic/claude-3"
        assert router.get_model("/test/daily/2024-01-15.md") == "qwen/qwen3.5-plus"
        assert router.get_model("/test/technical/code.py", "code") == "deepseek/deepseek-coder"


# ==============================================================================
# Edge Cases and Error Handling Tests
# ==============================================================================


class TestModelRouterEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file_path(self, basic_rules: list[RoutingRule], default_model: str) -> None:
        """Test handling of empty file path."""
        router = ModelRouter(rules=basic_rules, default_model=default_model)
        model = router.get_model("")
        assert model == default_model

    def test_whitespace_only_path(self, default_model: str) -> None:
        """Test handling of whitespace-only path."""
        router = ModelRouter(rules=[], default_model=default_model)
        model = router.get_model("   ")
        assert model == default_model

    def test_relative_path(self, basic_rules: list[RoutingRule], default_model: str) -> None:
        """Test handling of relative file path."""
        router = ModelRouter(rules=basic_rules, default_model=default_model)
        model = router.get_model("drafts/note.md")
        assert model == "openai/gpt-4"

    def test_path_with_trailing_slash(self, default_model: str) -> None:
        """Test handling of path with trailing slash (directory path)."""
        rules = [RoutingRule(pattern="**/drafts/*", model="openai/gpt-4")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # A directory path doesn't match a file pattern
        model = router.get_model("/test/drafts/")
        assert model == default_model

    def test_path_with_backslashes_windows_style(self, default_model: str) -> None:
        """Test handling of Windows-style paths with backslashes."""
        rules = [RoutingRule(pattern="**/drafts/*", model="openai/gpt-4")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Windows-style path - fnmatch works with forward slashes
        # Our implementation should handle this consistently
        model = router.get_model("C:\\Users\\test\\drafts\\note.md")
        # Behavior depends on implementation - should handle gracefully
        # Either normalize the path or return default
        assert model in ["openai/gpt-4", default_model]

    def test_very_long_path(self, default_model: str) -> None:
        """Test handling of very long file paths."""
        rules = [RoutingRule(pattern="**/*.md", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        long_path = "/a/" * 100 + "note.md"
        model = router.get_model(long_path)
        assert model == "anthropic/claude-3"

    def test_path_with_newline_characters(self, default_model: str) -> None:
        """Test handling of path with newline characters."""
        rules = [RoutingRule(pattern="**/*.md", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Path with newline - unusual but should not crash
        model = router.get_model("/test/note\n.md")
        # Implementation should handle gracefully
        assert model in ["anthropic/claude-3", default_model]

    def test_pattern_with_question_mark(self, default_model: str) -> None:
        """Test pattern with question mark single char wildcard."""
        rules = [RoutingRule(pattern="**/note?.md", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        assert router.get_model("/test/note1.md") == "anthropic/claude-3"
        assert router.get_model("/test/noteA.md") == "anthropic/claude-3"
        assert router.get_model("/test/note.md") == default_model  # No single char
        assert router.get_model("/test/note12.md") == default_model  # Two chars

    def test_pattern_with_character_class(self, default_model: str) -> None:
        """Test pattern with character class [abc]."""
        rules = [RoutingRule(pattern="**/note[123].md", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        assert router.get_model("/test/note1.md") == "anthropic/claude-3"
        assert router.get_model("/test/note2.md") == "anthropic/claude-3"
        assert router.get_model("/test/note4.md") == default_model

    def test_multiple_rules_same_pattern(self, default_model: str) -> None:
        """Test that when multiple rules have same pattern, first wins."""
        rules = [
            RoutingRule(pattern="**/*.md", model="model-a"),
            RoutingRule(pattern="**/*.md", model="model-b"),
            RoutingRule(pattern="**/*.md", model="model-c"),
        ]
        router = ModelRouter(rules=rules, default_model=default_model)

        # First rule should win
        assert router.get_model("/test/note.md") == "model-a"

    def test_rule_with_empty_task_types_list(self, default_model: str) -> None:
        """Test rule with explicitly empty task types list."""
        rules = [
            RoutingRule(
                pattern="**/*.md",
                model="anthropic/claude-3",
                task_types=(),  # Empty tuple
            )
        ]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Empty task types means no filtering - should match any task type
        assert router.get_model("/test/note.md", None) is True or \
               router.get_model("/test/note.md", None) == "anthropic/claude-3"

    def test_config_with_extra_fields(self, default_model: str) -> None:
        """Test config with extra fields in rules (should be ignored)."""
        config = {
            "rules": [
                {
                    "pattern": "**/*.md",
                    "model": "anthropic/claude-3",
                    "extra_field": "ignored",  # Should be ignored
                    "another_field": 123,
                }
            ]
        }
        router = ModelRouter.from_config(config, default_model)
        assert len(router.rules) == 1
        assert router.rules[0].model == "anthropic/claude-3"

    def test_config_with_invalid_rule_entries(self, default_model: str) -> None:
        """Test config with invalid rule entries (non-dict types)."""
        config = {
            "rules": [
                "invalid_string_rule",  # Should be skipped
                123,  # Should be skipped
                None,  # Should be skipped
                {"pattern": "**/*.md", "model": "valid/model"},  # Valid
                ["list", "not", "dict"],  # Should be skipped
            ]
        }
        router = ModelRouter.from_config(config, default_model)
        assert len(router.rules) == 1
        assert router.rules[0].model == "valid/model"

    def test_simple_glob_multiple_components(self, default_model: str) -> None:
        """Test simple glob matching with multiple path components.

        This tests the component-wise matching in _match_simple_glob.
        """
        rules = [RoutingRule(pattern="test/notes/*.md", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Should match - same number of components
        assert router.get_model("test/notes/note.md") == "anthropic/claude-3"

        # Should not match - different number of components
        assert router.get_model("test/note.md") == default_model
        assert router.get_model("test/notes/subdir/note.md") == default_model

    def test_absolute_path_pattern(self, default_model: str) -> None:
        """Test pattern starting with / (absolute path pattern)."""
        rules = [RoutingRule(pattern="/test/*.md", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Should match absolute path pattern
        assert router.get_model("/test/note.md") == "anthropic/claude-3"
        assert router.get_model("/other/note.md") == default_model

    def test_absolute_path_pattern_with_globstar(self, default_model: str) -> None:
        """Test pattern starting with / combined with **.

        This tests the branch in _match_globstar that handles patterns starting with /.
        """
        rules = [RoutingRule(pattern="/test/**", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Should match absolute paths under /test/
        assert router.get_model("/test/note.md") == "anthropic/claude-3"
        assert router.get_model("/test/subdir/note.md") == "anthropic/claude-3"
        assert router.get_model("/other/note.md") == default_model


# ==============================================================================
# Performance Tests
# ==============================================================================


class TestModelRouterPerformance:
    """Tests for performance with many rules."""

    def test_many_rules(self, default_model: str) -> None:
        """Test router with many rules (100 rules)."""
        rules = [
            RoutingRule(pattern=f"**/dir{i}/*", model=f"model-{i}")
            for i in range(100)
        ]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Should still work efficiently
        model = router.get_model("/test/dir50/note.md")
        assert model == "model-50"

    def test_many_files_routing(self, default_model: str) -> None:
        """Test routing many files (should complete quickly)."""
        rules = [
            RoutingRule(pattern="**/drafts/*", model="openai/gpt-4"),
            RoutingRule(pattern="**/*.md", model="anthropic/claude-3"),
        ]
        router = ModelRouter(rules=rules, default_model=default_model)

        # Route 1000 files
        for i in range(1000):
            if i % 2 == 0:
                model = router.get_model(f"/test/drafts/note{i}.md")
                assert model == "openai/gpt-4"
            else:
                model = router.get_model(f"/test/notes/note{i}.md")
                assert model == "anthropic/claude-3"

    def test_deeply_nested_path(self, default_model: str) -> None:
        """Test routing with deeply nested path."""
        rules = [RoutingRule(pattern="**/target/*", model="anthropic/claude-3")]
        router = ModelRouter(rules=rules, default_model=default_model)

        deep_path = "/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/target/file.md"
        model = router.get_model(deep_path)
        assert model == "anthropic/claude-3"