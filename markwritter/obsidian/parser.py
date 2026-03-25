"""Note parser for Obsidian markdown files."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from markwritter.obsidian.models import Frontmatter, Note, NoteMeta


class NoteParser:
    """Parser for Obsidian markdown notes.

    Handles:
    - YAML frontmatter extraction
    - Wikilinks extraction ([[link]] and [[link|alias]])
    - Tags extraction
    """

    # Regex patterns
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    WIKILINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    TAG_PATTERN = re.compile(r"(?<![^\s])#([\w\-\/]+)")

    def __init__(self, vault_path: Path):
        """Initialize parser with vault root path.

        Args:
            vault_path: Root directory of the Obsidian vault
        """
        self.vault_path = vault_path

    def parse_frontmatter(self, content: str) -> Frontmatter:
        """Parse YAML frontmatter from note content.

        Args:
            content: Raw markdown content

        Returns:
            Frontmatter object with parsed data
        """
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            return Frontmatter(data={}, content_start=0)

        try:
            yaml_content = match.group(1)
            data = yaml.safe_load(yaml_content) or {}
            # Calculate where content starts (after frontmatter)
            content_start = content.count("\n", 0, match.end()) + 1
            return Frontmatter(data=data, content_start=content_start)
        except yaml.YAMLError:
            return Frontmatter(data={}, content_start=0)

    def extract_wikilinks(self, content: str) -> list[str]:
        """Extract wikilinks from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of linked note paths (relative to vault)
        """
        matches = self.WIKILINK_PATTERN.findall(content)
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for link in matches:
            link = link.strip()
            if link not in seen:
                seen.add(link)
                result.append(link)
        return result

    def extract_tags(self, content: str) -> list[str]:
        """Extract tags from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of tags (without # prefix)
        """
        matches = self.TAG_PATTERN.findall(content)
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for tag in matches:
            if tag not in seen:
                seen.add(tag)
                result.append(tag)
        return result

    def _get_file_modified_time(self, path: Path) -> Optional[datetime]:
        """Get file modification time as datetime."""
        try:
            return datetime.fromtimestamp(path.stat().st_mtime)
        except (OSError, AttributeError):
            return None

    def parse_note(self, path: Path) -> Note:
        """Parse a note file into a Note object.

        Args:
            path: Absolute path to the note file

        Returns:
            Parsed Note object
        """
        content = path.read_text(encoding="utf-8")
        frontmatter = self.parse_frontmatter(content)

        # Get relative path from vault root
        relative_path = str(path.relative_to(self.vault_path))

        # Extract content after frontmatter
        if frontmatter.content_start > 0:
            # Find end of frontmatter in content
            match = self.FRONTMATTER_PATTERN.match(content)
            if match:
                body_content = content[match.end() :]
            else:
                body_content = content
        else:
            body_content = content

        # Extract links and tags
        links = self.extract_wikilinks(body_content)
        tags = self.extract_tags(body_content)

        # Merge tags from frontmatter and body
        metadata = dict(frontmatter.data)
        if "tags" in metadata:
            if isinstance(metadata["tags"], str):
                fm_tags = [metadata["tags"]]
            else:
                fm_tags = list(metadata["tags"])
        else:
            fm_tags = []

        # Combine and deduplicate tags
        all_tags = list(dict.fromkeys(fm_tags + tags))
        metadata["tags"] = all_tags

        # Get file timestamps
        modified = self._get_file_modified_time(path)

        return Note(
            path=relative_path,
            content=body_content,
            metadata=metadata,
            links=links,
            backlinks=[],  # Backlinks are computed by Vault
            modified=modified,
        )

    def parse_note_meta(self, path: Path) -> NoteMeta:
        """Parse lightweight metadata from a note file.

        Args:
            path: Absolute path to the note file

        Returns:
            NoteMeta object with basic info
        """
        content = path.read_text(encoding="utf-8")
        frontmatter = self.parse_frontmatter(content)

        # Get relative path from vault root
        relative_path = str(path.relative_to(self.vault_path))

        # Extract title
        title = frontmatter.data.get("title")
        if not title:
            # Fallback to filename without extension
            title = path.stem

        # Extract tags
        if "tags" in frontmatter.data:
            if isinstance(frontmatter.data["tags"], str):
                tags = [frontmatter.data["tags"]]
            else:
                tags = list(frontmatter.data["tags"])
        else:
            tags = []

        # Get file timestamps
        modified = self._get_file_modified_time(path)

        return NoteMeta(
            path=relative_path,
            title=str(title) if title else None,
            tags=tags,
            modified=modified,
        )
