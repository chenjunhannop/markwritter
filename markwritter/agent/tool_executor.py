# Tool executor for agent loop.
# Maps Anthropic tool call names to ObsidianVault operations.

import json
import logging
import traceback
from pathlib import Path
from typing import Any

from markwritter.obsidian.vault import ObsidianVault

logger = logging.getLogger(__name__)

_IGNORED_DIRS = frozenset({
    "node_modules", "venv", ".venv", "__pycache__", ".git",
    ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "dist", "build", ".next", ".nuxt", "coverage",
})


def _serialize_meta(meta: Any) -> dict[str, Any]:
    return {"path": meta.path, "title": meta.title, "tags": meta.tags}


def _serialize_note(note: Any) -> dict[str, Any]:
    return {
        "path": note.path,
        "title": note.metadata.get("title", Path(note.path).stem),
        "content": note.content,
        "metadata": note.metadata,
        "tags": note.metadata.get("tags", []),
        "backlinks": note.backlinks,
    }


def _is_safe_path(path: str) -> bool:
    if not path:
        return False
    if "\x00" in path:
        return False
    if ".." in path.replace("\\", "/"):
        return False
    if "~" in path:
        return False
    from pathlib import PurePath
    try:
        if PurePath(path).is_absolute():
            return False
    except Exception:
        return False
    return True


def _build_tree(directory: Path, prefix: str = "") -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    total_md = 0
    try:
        entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return {"tree": [], "file_count": 0}

    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.name in _IGNORED_DIRS:
            continue
        rel = f"{prefix}/{entry.name}" if prefix else entry.name
        if entry.is_dir():
            sub = _build_tree(entry, rel)
            total_md += sub.get("file_count", 0)
            items.append({
                "name": entry.name,
                "path": rel,
                "type": "directory",
                "file_count": sub.get("file_count", 0),
                "children": sub.get("tree", []),
            })
        elif entry.suffix.lower() == ".md":
            total_md += 1
            items.append({"name": entry.name, "path": rel, "type": "file"})

    return {"tree": items, "file_count": total_md}


class ToolExecutor:

    def __init__(self, vault: ObsidianVault) -> None:
        self._vault = vault

    def execute(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        dispatch = {
            "read_note": self._exec_read_note,
            "search_notes": self._exec_search_notes,
            "list_notes": self._exec_list_notes,
            "write_note": self._exec_write_note,
            "delete_note": self._exec_delete_note,
            "get_file_tree": self._exec_get_file_tree,
        }
        handler = dispatch.get(tool_name)
        if handler is None:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        try:
            result = handler(tool_input)
            return json.dumps(result, ensure_ascii=False)
        except Exception as exc:
            logger.error("Tool execution error %s: %s", tool_name, exc)
            logger.debug(traceback.format_exc())
            return json.dumps({"error": str(exc)})

    def _exec_read_note(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params.get("path", "")
        if not _is_safe_path(path):
            return {"error": "Invalid path: path traversal not allowed"}
        note = self._vault.read_note(path)
        return _serialize_note(note)

    def _exec_search_notes(self, params: dict[str, Any]) -> dict[str, Any]:
        query = params.get("query", "")
        results = self._vault.search_by_keyword(query)
        return {"results": [_serialize_meta(n) for n in results], "count": len(results)}

    def _exec_list_notes(self, params: dict[str, Any]) -> dict[str, Any]:
        directory = params.get("directory")
        recursive = params.get("recursive", True)
        notes = self._vault.list_notes(directory=directory, recursive=recursive)
        return {"notes": [_serialize_meta(n) for n in notes], "count": len(notes)}

    def _exec_write_note(self, params: dict[str, Any]) -> dict[str, Any]:
        from markwritter.obsidian.models import Note

        path = params.get("path", "")
        content = params.get("content", "")
        overwrite = params.get("overwrite", True)

        if not _is_safe_path(path):
            return {"error": "Invalid path: path traversal not allowed"}

        note = Note(path=path, content=content, metadata={})
        self._vault.write_note(note, overwrite=overwrite)
        return {"success": True, "path": path}

    def _exec_delete_note(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params.get("path", "")
        if not _is_safe_path(path):
            return {"error": "Invalid path: path traversal not allowed"}
        self._vault.delete_note(path)
        return {"success": True, "path": path}

    def _exec_get_file_tree(self, _params: dict[str, Any]) -> dict[str, Any]:
        return _build_tree(self._vault.path)
