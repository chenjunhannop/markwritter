"""Anthropic-format tool definitions for vault operations.

These definitions are sent to the LLM so it can call vault operations
(read, write, search, list, etc.) during the agent loop.
"""

from typing import Any


def get_vault_tools() -> list[dict[str, Any]]:
    """Return the list of Anthropic-format tool definitions.

    Each tool follows the Anthropic Messages API tool schema:
    https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    """
    return [
        {
            "name": "read_note",
            "description": (
                "Read the full content of a note in the vault. "
                "Returns the note content including any YAML frontmatter. "
                "Use this when you need to see what a note contains."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the note from vault root (e.g. 'ideas/project.md')",
                    }
                },
                "required": ["path"],
            },
        },
        {
            "name": "list_notes",
            "description": (
                "List notes in a vault directory. Returns matching file paths. "
                "Use this to browse what notes exist before reading them."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Relative directory path to list. Omit to list vault root.",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Include subdirectories. Default: true.",
                        "default": True,
                    },
                },
                "required": [],
            },
        },
        {
            "name": "search_notes",
            "description": (
                "Search vault notes by keyword. Returns matching file paths with titles. "
                "Use this to find notes related to a topic."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword or phrase to search for in note content.",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "write_note",
            "description": (
                "Create or overwrite a note in the vault. "
                "Use this to save new content or update existing notes. "
                "Set overwrite=true to replace an existing note."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path for the note (e.g. 'ideas/new-idea.md')",
                    },
                    "content": {
                        "type": "string",
                        "description": "The markdown content to write.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite if the note already exists. Default: true.",
                        "default": True,
                    },
                },
                "required": ["path", "content"],
            },
        },
        {
            "name": "get_file_tree",
            "description": (
                "Get the vault file tree structure. Returns nested directory listing "
                "with file counts per directory. Use this to understand the vault layout."
            ),
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]
