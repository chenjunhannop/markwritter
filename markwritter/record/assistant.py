"""AI Writing Assistant and Auto Classification.

This module provides:
- WritingAssistant: AI-powered writing assistance (continue, rewrite, polish)
- AutoClassifier: Automatic note classification and tagging
"""

from __future__ import annotations

import json
import inspect
import logging
import re
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from markwritter.llm_client import LLMClient

logger = logging.getLogger(__name__)


# ==============================================================================
# Models
# ==============================================================================


class ClassifyResult(BaseModel):
    """Result of content classification."""

    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: Optional[str] = None


# ==============================================================================
# Writing Assistant
# ==============================================================================


class WritingAssistant:
    """AI-powered writing assistant for note content.

    Provides:
    - continue_writing: Continue the text from where it left off
    - rewrite: Rewrite text in a different style
    - polish: Improve grammar, clarity, and flow
    """

    # Prompts for different operations
    CONTINUE_PROMPT = """You are a writing assistant. Continue the following text naturally, maintaining the same tone and style. Only provide the continuation, not the original text.

Text to continue:
{content}

Continuation:"""

    REWRITE_PROMPT = """You are a writing assistant. Rewrite the following text in a {style} style. Preserve the original meaning while changing the tone and language to match the requested style.

Original text:
{content}

Rewritten text in {style} style:"""

    POLISH_PROMPT = """You are an editor. Improve the following text by:
1. Fixing grammar and spelling errors
2. Improving clarity and readability
3. Enhancing the flow between sentences
4. Maintaining the original meaning and tone
5. Preserving any code blocks, links, or markdown formatting

Original text:
{content}

Polished text:"""

    # Supported rewrite styles
    STYLES = ["formal", "casual", "academic", "creative", "concise"]

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        max_tokens: int = 500,
    ) -> None:
        """Initialize the writing assistant.

        Args:
            llm_client: LLM client for text generation. If None, creates default.
            max_tokens: Maximum tokens for generated text.
        """
        if llm_client is None:
            from markwritter.llm_client import LLMClient

            llm_client = LLMClient()

        self.llm_client = llm_client
        self.max_tokens = max_tokens

    def continue_writing(
        self,
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Continue writing from the given content.

        Args:
            content: The existing content to continue from.
            max_tokens: Maximum tokens for continuation.

        Returns:
            The continuation text.
        """
        if not content or not content.strip():
            return "Please provide some content to continue from."

        prompt = self.CONTINUE_PROMPT.format(content=content)
        tokens = max_tokens or self.max_tokens

        try:
            result = self.llm_client.complete(prompt, max_tokens=tokens)
            return result.strip()
        except Exception as e:
            logger.error(f"Error in continue_writing: {e}")
            return f"Error generating continuation: {str(e)}"

    async def continue_writing_stream(
        self,
        content: str,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Continue writing with streaming output.

        Args:
            content: The existing content to continue from.
            max_tokens: Maximum tokens for continuation.

        Yields:
            Chunks of the continuation text.
        """
        if not content or not content.strip():
            yield "Please provide some content to continue from."
            return

        prompt = self.CONTINUE_PROMPT.format(content=content)
        tokens = max_tokens or self.max_tokens

        try:
            stream_complete = getattr(self.llm_client, "stream_complete", None)
            if callable(stream_complete):
                stream = stream_complete(prompt, max_tokens=tokens)
                if inspect.isasyncgen(stream):
                    async for chunk in stream:
                        yield chunk
                    return

            # Fallback to non-streaming
            result = self.llm_client.complete(prompt, max_tokens=tokens)
            yield result.strip()
        except Exception as e:
            logger.error(f"Error in continue_writing_stream: {e}")
            yield f"Error generating continuation: {str(e)}"

    def rewrite(
        self,
        content: str,
        style: str = "formal",
        max_tokens: Optional[int] = None,
    ) -> str:
        """Rewrite content in a different style.

        Args:
            content: The content to rewrite.
            style: The target style (formal, casual, academic, creative, concise).
            max_tokens: Maximum tokens for output.

        Returns:
            The rewritten text.
        """
        if not content or not content.strip():
            return "Please provide content to rewrite."

        style = style.lower()
        if style not in self.STYLES:
            style = "formal"  # Default fallback

        prompt = self.REWRITE_PROMPT.format(content=content, style=style)
        tokens = max_tokens or self.max_tokens

        try:
            result = self.llm_client.chat_complete(
                [{"role": "user", "content": prompt}],
                max_tokens=tokens,
            )
            return result.strip()
        except Exception as e:
            logger.error(f"Error in rewrite: {e}")
            return f"Error rewriting content: {str(e)}"

    def polish(
        self,
        content: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Polish content for better clarity and grammar.

        Args:
            content: The content to polish.
            max_tokens: Maximum tokens for output.

        Returns:
            The polished text.
        """
        if not content or not content.strip():
            return "Please provide content to polish."

        prompt = self.POLISH_PROMPT.format(content=content)
        tokens = max_tokens or self.max_tokens

        try:
            result = self.llm_client.chat_complete(
                [{"role": "user", "content": prompt}],
                max_tokens=tokens,
            )
            return result.strip()
        except Exception as e:
            logger.error(f"Error in polish: {e}")
            return f"Error polishing content: {str(e)}"


# ==============================================================================
# Auto Classifier
# ==============================================================================


class AutoClassifier:
    """Automatic note classification and suggestion system.

    Provides:
    - classify: Classify content into categories
    - suggest_tags: Suggest relevant tags for content
    - suggest_folder: Suggest a folder path for the note
    - suggest_links: Suggest related notes to link to
    """

    CLASSIFY_PROMPT = """You are a content classifier. Classify the following content into one of these categories:
{categories}

Return a JSON object with:
- "category": the best matching category
- "confidence": a number between 0 and 1 indicating confidence
- "reasoning": brief explanation (optional)

Content:
{content}

Response (JSON only):"""

    TAGS_PROMPT = """You are a tag suggestion assistant. Suggest relevant tags for the following content.

Rules:
- Tags should be lowercase
- Tags should not contain spaces (use hyphens)
- Suggest 3-7 relevant tags
- Consider topics, technologies, concepts mentioned

Return a JSON array of tag strings.

Content:
{content}

Existing tags (if any): {existing_tags}

Response (JSON array only):"""

    FOLDER_PROMPT = """You are a folder organization assistant. Suggest the best folder path for a note with the following content.

Rules:
- Use lowercase folder names
- Use forward slashes for nested folders (e.g., "projects/python")
- Do not start with a slash
- Keep folder names short and descriptive

Return only the folder path string (no JSON, just the path).

Content:
{content}

Existing folder structure: {existing_folders}

Folder path:"""

    LINKS_PROMPT = """You are a note linking assistant. Given content and a list of existing notes, suggest which notes should be linked.

Return a JSON array of note paths that are most relevant to the content.

Content:
{content}

Existing notes:
{existing_notes}

Maximum links: {max_links}

Response (JSON array only):"""

    # Default categories
    DEFAULT_CATEGORIES = [
        "programming",
        "learning",
        "personal",
        "work",
        "projects",
        "daily",
        "resources",
        "ideas",
        "meetings",
        "reference",
    ]

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        categories: Optional[list[str]] = None,
    ) -> None:
        """Initialize the auto classifier.

        Args:
            llm_client: LLM client for classification. If None, creates default.
            categories: List of valid categories for classification.
        """
        if llm_client is None:
            from markwritter.llm_client import LLMClient

            llm_client = LLMClient()

        self.llm_client = llm_client
        self.categories = categories or self.DEFAULT_CATEGORIES

    def classify(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ClassifyResult:
        """Classify content into a category.

        Args:
            content: The content to classify.
            metadata: Optional existing metadata to consider.

        Returns:
            Classification result with category and confidence.
        """
        if not content or not content.strip():
            return ClassifyResult(category="uncategorized", confidence=0.0)

        # Check for daily note patterns
        if self._is_daily_note(content):
            return ClassifyResult(category="daily", confidence=0.95)

        prompt = self.CLASSIFY_PROMPT.format(
            categories=", ".join(self.categories),
            content=content[:2000],  # Limit content length
        )

        try:
            result = self.llm_client.complete(prompt, max_tokens=200)
            return self._parse_classify_result(result)
        except Exception as e:
            logger.error(f"Error in classify: {e}")
            return ClassifyResult(category="uncategorized", confidence=0.0)

    def _is_daily_note(self, content: str) -> bool:
        """Check if content looks like a daily note."""
        # Check for date patterns
        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}",  # 2024-01-15
            r"^#\s*\d{4}-\d{2}-\d{2}",  # # 2024-01-15
            r"^##\s*(Morning|Afternoon|Evening)",  # ## Morning
            r"^##\s*\d{4}",  # ## 2024
        ]

        for pattern in date_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False

    def _parse_classify_result(self, result: str) -> ClassifyResult:
        """Parse classification result from LLM response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{[^{}]*\}", result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                category = data.get("category", "uncategorized")
                confidence = float(data.get("confidence", 0.5))
                reasoning = data.get("reasoning")

                # Validate category
                if category not in self.categories:
                    category = self._find_closest_category(category)

                return ClassifyResult(
                    category=category,
                    confidence=min(1.0, max(0.0, confidence)),
                    reasoning=reasoning,
                )
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse classify result: {e}")

        return ClassifyResult(category="uncategorized", confidence=0.0)

    def _find_closest_category(self, category: str) -> str:
        """Find the closest matching category."""
        category_lower = category.lower()
        for valid_cat in self.categories:
            if category_lower in valid_cat or valid_cat in category_lower:
                return valid_cat
        return "uncategorized"

    def suggest_tags(
        self,
        content: str,
        existing_tags: Optional[list[str]] = None,
        max_tags: int = 5,
    ) -> list[str]:
        """Suggest tags for content.

        Args:
            content: The content to analyze.
            existing_tags: Existing tags to consider.
            max_tags: Maximum number of tags to return.

        Returns:
            List of suggested tags.
        """
        if not content or not content.strip():
            return []

        existing_str = ", ".join(existing_tags) if existing_tags else "none"
        prompt = self.TAGS_PROMPT.format(
            content=content[:1500],
            existing_tags=existing_str,
        )

        try:
            result = self.llm_client.complete(prompt, max_tokens=200)
            tags = self._parse_tags_result(result)

            # Deduplicate (case-insensitive)
            seen = set()
            unique_tags = []
            for tag in tags:
                tag_lower = tag.lower()
                if tag_lower not in seen:
                    seen.add(tag_lower)
                    unique_tags.append(tag_lower)

            return unique_tags[:max_tags]
        except Exception as e:
            logger.error(f"Error in suggest_tags: {e}")
            return []

    def _parse_tags_result(self, result: str) -> list[str]:
        """Parse tags from LLM response."""
        try:
            # Try to extract JSON array
            json_match = re.search(r"\[[^\]]*\]", result, re.DOTALL)
            if json_match:
                tags = json.loads(json_match.group())
                if isinstance(tags, list):
                    return [self._normalize_tag(str(tag)) for tag in tags if tag]
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse tags result: {e}")

        return []

    def _normalize_tag(self, tag: str) -> str:
        """Normalize a tag string."""
        # Remove # prefix if present
        tag = tag.lstrip("#")
        # Convert to lowercase
        tag = tag.lower().strip()
        # Replace spaces with hyphens
        tag = re.sub(r"\s+", "-", tag)
        return tag

    def suggest_folder(
        self,
        content: str,
        existing_folders: Optional[list[str]] = None,
    ) -> str:
        """Suggest a folder path for the content.

        Args:
            content: The content to analyze.
            existing_folders: Existing folder structure to consider.

        Returns:
            Suggested folder path.
        """
        if not content or not content.strip():
            return "inbox"

        # Check for daily note
        if self._is_daily_note(content):
            return "daily"

        existing_str = "\n".join(existing_folders[:20]) if existing_folders else "none"
        prompt = self.FOLDER_PROMPT.format(
            content=content[:1000],
            existing_folders=existing_str,
        )

        try:
            result = self.llm_client.complete(prompt, max_tokens=100)
            folder = result.strip().strip("\"'")

            # Validate folder path
            folder = self._normalize_folder(folder)
            return folder
        except Exception as e:
            logger.error(f"Error in suggest_folder: {e}")
            return "inbox"

    def _normalize_folder(self, folder: str) -> str:
        """Normalize a folder path."""
        # Remove leading slashes
        folder = folder.lstrip("/")
        # Remove invalid characters
        folder = re.sub(r'[<>:"|?*]', "", folder)
        # Normalize slashes
        folder = re.sub(r"[/\\]+", "/", folder)
        # Lowercase
        folder = folder.lower()
        return folder or "inbox"

    def suggest_links(
        self,
        content: str,
        existing_notes: list[str],
        max_links: int = 5,
    ) -> list[str]:
        """Suggest related notes to link to.

        Args:
            content: The content to analyze.
            existing_notes: List of existing note paths.
            max_links: Maximum number of links to suggest.

        Returns:
            List of suggested note paths to link to.
        """
        if not content or not content.strip() or not existing_notes:
            return []

        notes_str = "\n".join(existing_notes[:50])  # Limit for prompt
        prompt = self.LINKS_PROMPT.format(
            content=content[:1000],
            existing_notes=notes_str,
            max_links=max_links,
        )

        try:
            result = self.llm_client.complete(prompt, max_tokens=200)
            links = self._parse_links_result(result)

            # Filter to only include existing notes
            valid_links = [link for link in links if link in existing_notes]
            return valid_links[:max_links]
        except Exception as e:
            logger.error(f"Error in suggest_links: {e}")
            return []

    def _parse_links_result(self, result: str) -> list[str]:
        """Parse links from LLM response."""
        try:
            # Try to extract JSON array
            json_match = re.search(r"\[[^\]]*\]", result, re.DOTALL)
            if json_match:
                links = json.loads(json_match.group())
                if isinstance(links, list):
                    return [str(link).strip("\"'") for link in links if link]
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse links result: {e}")

        return []
