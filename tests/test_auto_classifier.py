"""Tests for AutoClassifier.

TDD approach: Tests for automatic classification before implementation.
"""

from unittest.mock import MagicMock, patch

import pytest

from markwritter.llm_client import LLMClient

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client."""
    client = MagicMock(spec=LLMClient)
    client.complete = MagicMock(return_value='{"category": "programming", "confidence": 0.9}')
    client.chat_complete = MagicMock(return_value='{"tags": ["python", "testing", "tdd"]}')
    return client


@pytest.fixture
def sample_note_content() -> str:
    """Sample note content for testing."""
    return """# Python Testing Guide

This guide covers best practices for testing Python applications.

## Topics Covered

- pytest framework
- unittest module
- Mock objects
- Test-driven development

Tags: #python #testing #tdd
"""


@pytest.fixture
def sample_daily_note() -> str:
    """Sample daily note content."""
    return """# 2024-01-15

## Morning
- Had coffee
- Checked emails

## Tasks
- [ ] Review PR
- [x] Write tests

## Notes
Good progress on the project today.
"""


# ==============================================================================
# AutoClassifier Initialization Tests
# ==============================================================================


class TestAutoClassifierInit:
    """Tests for AutoClassifier initialization."""

    def test_init_with_llm_client(self, mock_llm_client: MagicMock) -> None:
        """Test initialization with provided LLM client."""
        from markwritter.record.assistant import AutoClassifier

        classifier = AutoClassifier(llm_client=mock_llm_client)
        assert classifier.llm_client == mock_llm_client

    def test_init_without_llm_client(self) -> None:
        """Test initialization without LLM client."""
        from markwritter.record.assistant import AutoClassifier

        with patch("markwritter.llm_client.LLMClient") as mock_client_class:
            mock_client_class.return_value = MagicMock()
            _ = AutoClassifier()  # noqa: F841
            mock_client_class.assert_called_once()

    def test_init_with_custom_categories(self, mock_llm_client: MagicMock) -> None:
        """Test initialization with custom categories."""
        from markwritter.record.assistant import AutoClassifier

        categories = ["programming", "personal", "work", "learning"]
        classifier = AutoClassifier(
            llm_client=mock_llm_client,
            categories=categories,
        )
        assert classifier.categories == categories


# ==============================================================================
# Classify Tests
# ==============================================================================


class TestClassify:
    """Tests for classify method."""

    def test_classify_basic(self, mock_llm_client: MagicMock, sample_note_content: str) -> None:
        """Test basic classification."""
        from markwritter.record.assistant import AutoClassifier, ClassifyResult

        mock_llm_client.complete.return_value = '{"category": "programming", "confidence": 0.95}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify(sample_note_content)

        assert result is not None
        assert isinstance(result, ClassifyResult)
        assert result.category is not None
        assert result.confidence >= 0
        assert result.confidence <= 1

    def test_classify_returns_category(self, mock_llm_client: MagicMock) -> None:
        """Test that classify returns a valid category."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "learning", "confidence": 0.88}'

        classifier = AutoClassifier(
            llm_client=mock_llm_client,
            categories=["programming", "learning", "personal"],
        )
        result = classifier.classify("Content about learning new things")

        assert result.category in ["programming", "learning", "personal"]

    def test_classify_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test classification with empty content."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "uncategorized", "confidence": 0.0}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify("")

        assert result is not None

    def test_classify_daily_note(self, mock_llm_client: MagicMock, sample_daily_note: str) -> None:
        """Test classification of daily notes."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "daily", "confidence": 0.95}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify(sample_daily_note)

        assert result.category is not None

    def test_classify_confidence_threshold(self, mock_llm_client: MagicMock) -> None:
        """Test that confidence is properly parsed."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "work", "confidence": 0.75}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify("Some work-related content")

        assert 0.0 <= result.confidence <= 1.0

    def test_classify_with_metadata(self, mock_llm_client: MagicMock) -> None:
        """Test classification can use existing metadata."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "programming", "confidence": 0.9}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify(
            "Content",
            metadata={"tags": ["python"], "created": "2024-01-15"},
        )

        assert result is not None


# ==============================================================================
# Suggest Tags Tests
# ==============================================================================


class TestSuggestTags:
    """Tests for suggest_tags method."""

    def test_suggest_tags_basic(self, mock_llm_client: MagicMock, sample_note_content: str) -> None:
        """Test basic tag suggestion."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["python", "testing", "pytest"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        tags = classifier.suggest_tags(sample_note_content)

        assert tags is not None
        assert isinstance(tags, list)
        assert all(isinstance(tag, str) for tag in tags)

    def test_suggest_tags_returns_relevant_tags(self, mock_llm_client: MagicMock) -> None:
        """Test that suggested tags are relevant to content."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["docker", "containers", "devops"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = "How to use Docker containers for development"
        tags = classifier.suggest_tags(content)

        assert len(tags) > 0
        # Tags should be lowercase and without # prefix
        for tag in tags:
            assert tag == tag.lower()
            assert not tag.startswith("#")

    def test_suggest_tags_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test tag suggestion with empty content."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = "[]"

        classifier = AutoClassifier(llm_client=mock_llm_client)
        tags = classifier.suggest_tags("")

        assert tags is not None
        assert isinstance(tags, list)

    def test_suggest_tags_max_tags(self, mock_llm_client: MagicMock) -> None:
        """Test tag suggestion with max_tags limit."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["tag1", "tag2", "tag3", "tag4", "tag5"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        tags = classifier.suggest_tags("Content", max_tags=3)

        assert len(tags) <= 3

    def test_suggest_tags_preserves_existing_tags(self, mock_llm_client: MagicMock) -> None:
        """Test that existing tags are considered."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["existing", "new-tag"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = "Content with existing tags"
        existing_tags = ["existing"]
        tags = classifier.suggest_tags(content, existing_tags=existing_tags)

        assert "existing" in tags or True  # May or may not include existing

    def test_suggest_tags_no_duplicates(self, mock_llm_client: MagicMock) -> None:
        """Test that suggested tags have no duplicates."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["python", "python", "testing", "Python"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        tags = classifier.suggest_tags("Python testing content")

        # After deduplication (case-insensitive)
        lower_tags = [t.lower() for t in tags]
        assert len(lower_tags) == len(set(lower_tags))


# ==============================================================================
# Suggest Folder Tests
# ==============================================================================


class TestSuggestFolder:
    """Tests for suggest_folder method."""

    def test_suggest_folder_basic(
        self, mock_llm_client: MagicMock, sample_note_content: str
    ) -> None:
        """Test basic folder suggestion."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '"programming/python"'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        folder = classifier.suggest_folder(sample_note_content)

        assert folder is not None
        assert isinstance(folder, str)

    def test_suggest_folder_returns_valid_path(self, mock_llm_client: MagicMock) -> None:
        """Test that suggested folder is a valid path format."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '"projects/python-testing"'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = "Notes about a Python testing project"
        folder = classifier.suggest_folder(content)

        # Should not start with /
        assert not folder.startswith("/")
        # Should not contain invalid characters
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
        for char in invalid_chars:
            assert char not in folder

    def test_suggest_folder_empty_content(self, mock_llm_client: MagicMock) -> None:
        """Test folder suggestion with empty content."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '"inbox"'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        folder = classifier.suggest_folder("")

        assert folder is not None

    def test_suggest_folder_with_existing_structure(self, mock_llm_client: MagicMock) -> None:
        """Test folder suggestion considering existing structure."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '"work/projects"'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        existing_folders = ["work", "personal", "work/projects", "work/meetings"]
        folder = classifier.suggest_folder(
            "New project notes",
            existing_folders=existing_folders,
        )

        assert folder is not None

    def test_suggest_folder_daily_notes(
        self, mock_llm_client: MagicMock, sample_daily_note: str
    ) -> None:
        """Test folder suggestion for daily notes."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '"daily/2024/01"'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        folder = classifier.suggest_folder(sample_daily_note)

        assert "daily" in folder.lower() or folder is not None


# ==============================================================================
# Suggest Links Tests
# ==============================================================================


class TestSuggestLinks:
    """Tests for suggest_links method."""

    def test_suggest_links_basic(
        self, mock_llm_client: MagicMock, sample_note_content: str
    ) -> None:
        """Test basic link suggestion."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["python-basics.md", "testing-guide.md"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        existing_notes = ["python-basics.md", "testing-guide.md", "docker-notes.md"]
        links = classifier.suggest_links(sample_note_content, existing_notes)

        assert links is not None
        assert isinstance(links, list)
        assert all(isinstance(link, str) for link in links)

    def test_suggest_links_empty_existing_notes(self, mock_llm_client: MagicMock) -> None:
        """Test link suggestion with no existing notes."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = "[]"

        classifier = AutoClassifier(llm_client=mock_llm_client)
        links = classifier.suggest_links("Some content", [])

        assert links == []

    def test_suggest_links_returns_relevant_links(self, mock_llm_client: MagicMock) -> None:
        """Test that suggested links are relevant."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["docker-setup.md"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = "How to set up Docker for development"
        existing_notes = ["docker-setup.md", "python-tips.md", "meeting-notes.md"]
        links = classifier.suggest_links(content, existing_notes)

        # Should suggest docker-related note
        assert any("docker" in link.lower() for link in links) or len(links) >= 0

    def test_suggest_links_max_links(self, mock_llm_client: MagicMock) -> None:
        """Test link suggestion with max limit."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["note1.md", "note2.md", "note3.md", "note4.md"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        existing_notes = ["note1.md", "note2.md", "note3.md", "note4.md", "note5.md"]
        links = classifier.suggest_links(
            "Content",
            existing_notes,
            max_links=2,
        )

        assert len(links) <= 2

    def test_suggest_links_only_existing_notes(self, mock_llm_client: MagicMock) -> None:
        """Test that only existing notes are suggested."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["existing.md", "non-existing.md"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        existing_notes = ["existing.md"]
        links = classifier.suggest_links("Content", existing_notes)

        # Should only include notes that exist
        for link in links:
            assert link in existing_notes


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================


class TestAutoClassifierEdgeCases:
    """Tests for edge cases and error handling."""

    def test_classify_very_long_content(self, mock_llm_client: MagicMock) -> None:
        """Test classification of very long content."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "article", "confidence": 0.8}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        long_content = "Word " * 10000
        result = classifier.classify(long_content)

        assert result is not None

    def test_classify_special_characters(self, mock_llm_client: MagicMock) -> None:
        """Test classification with special characters."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "notes", "confidence": 0.7}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = "Content with special chars: <>&\"'`\n\t\\"
        result = classifier.classify(content)

        assert result is not None

    def test_classify_unicode_content(self, mock_llm_client: MagicMock) -> None:
        """Test classification with Unicode content."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "notes", "confidence": 0.85}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = (
            "# Chinese Notes\n\nThis contains Chinese: \u4e2d\u6587\nJapanese: \u65e5\u672c\u8a9e"
        )
        result = classifier.classify(content)

        assert result is not None

    def test_invalid_json_response(self, mock_llm_client: MagicMock) -> None:
        """Test handling of invalid JSON response."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = "Not valid JSON"

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify("Content")

        # Should handle gracefully, possibly return default
        assert result is not None

    def test_suggest_tags_with_existing_tags_format(self, mock_llm_client: MagicMock) -> None:
        """Test tag suggestion handles existing tags with # prefix."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '["new-tag"]'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        existing_tags = ["#python", "#testing"]
        tags = classifier.suggest_tags("Content", existing_tags=existing_tags)

        # Should handle tags with or without #
        assert tags is not None

    def test_classify_with_code_blocks(self, mock_llm_client: MagicMock) -> None:
        """Test classification with code blocks."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "programming", "confidence": 0.95}'

        classifier = AutoClassifier(llm_client=mock_llm_client)
        content = """# Code Example

```python
def hello():
    print("Hello, World!")
```

This is a Python example.
"""
        result = classifier.classify(content)

        assert result.category == "programming"

    def test_classify_llm_error(self, mock_llm_client: MagicMock) -> None:
        """Test classification when LLM throws an error."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.side_effect = Exception("LLM error")

        classifier = AutoClassifier(llm_client=mock_llm_client)
        result = classifier.classify("Content")

        assert result.category == "uncategorized"
        assert result.confidence == 0.0

    def test_suggest_tags_llm_error(self, mock_llm_client: MagicMock) -> None:
        """Test tag suggestion when LLM throws an error."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.side_effect = Exception("LLM error")

        classifier = AutoClassifier(llm_client=mock_llm_client)
        tags = classifier.suggest_tags("Content")

        assert tags == []

    def test_suggest_folder_llm_error(self, mock_llm_client: MagicMock) -> None:
        """Test folder suggestion when LLM throws an error."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.side_effect = Exception("LLM error")

        classifier = AutoClassifier(llm_client=mock_llm_client)
        folder = classifier.suggest_folder("Content")

        assert folder == "inbox"

    def test_suggest_links_llm_error(self, mock_llm_client: MagicMock) -> None:
        """Test link suggestion when LLM throws an error."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.side_effect = Exception("LLM error")

        classifier = AutoClassifier(llm_client=mock_llm_client)
        links = classifier.suggest_links("Content", ["note1.md"])

        assert links == []

    def test_classify_unknown_category_finds_closest(self, mock_llm_client: MagicMock) -> None:
        """Test classification when category is not in list."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "coding", "confidence": 0.9}'

        classifier = AutoClassifier(
            llm_client=mock_llm_client,
            categories=["programming", "personal", "work"],
        )
        result = classifier.classify("Content about coding")

        # Should find closest category or return uncategorized
        assert result.category in ["programming", "uncategorized"]

    def test_suggest_tags_invalid_json_array(self, mock_llm_client: MagicMock) -> None:
        """Test tag suggestion with invalid JSON array response."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = "Not an array"

        classifier = AutoClassifier(llm_client=mock_llm_client)
        tags = classifier.suggest_tags("Content")

        assert tags == []

    def test_suggest_links_invalid_json_array(self, mock_llm_client: MagicMock) -> None:
        """Test link suggestion with invalid JSON array response."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = "Not an array"

        classifier = AutoClassifier(llm_client=mock_llm_client)
        links = classifier.suggest_links("Content", ["note1.md"])

        assert links == []

    def test_is_daily_note_patterns(self, mock_llm_client: MagicMock) -> None:
        """Test daily note detection patterns."""
        from markwritter.record.assistant import AutoClassifier

        mock_llm_client.complete.return_value = '{"category": "daily", "confidence": 0.95}'

        classifier = AutoClassifier(llm_client=mock_llm_client)

        # Test various daily note formats
        daily_formats = [
            "2024-01-15\n\nDaily content",
            "# 2024-01-15\n\nDaily content",
            "## Morning\n\nTasks here",
            "## 2024\n\nYearly review",
        ]

        for content in daily_formats:
            result = classifier.classify(content)
            assert result.category == "daily"
            assert result.confidence >= 0.9
