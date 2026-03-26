"""Knowledge Graph functionality for Markwritter.

Provides:
- GraphData: Complete graph structure with nodes and edges
- GraphNode: Node representation for a note
- GraphEdge: Edge representation for a link between notes
- KnowledgeGraph: Graph builder and analyzer
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from markwritter.exceptions import InvalidVaultError, NodeNotFoundError
from markwritter.obsidian.models import NoteMeta
from markwritter.obsidian.parser import NoteParser


class GraphNode(BaseModel):
    """Node representation for a note in the knowledge graph."""

    id: str  # Note path (e.g., "notes/my-note.md")
    title: str
    path: str
    tags: list[str] = Field(default_factory=list)
    connections_count: int = 0  # Total incoming + outgoing connections


class GraphEdge(BaseModel):
    """Edge representation for a link between notes."""

    source: str  # Source note path
    target: str  # Target note path
    type: str = "wikilink"  # Link type (wikilink, backlink, etc.)
    weight: float = 1.0  # Edge weight


class GraphData(BaseModel):
    """Complete graph structure with nodes and edges."""

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class KnowledgeGraph:
    """Knowledge graph builder and analyzer.

    Provides:
    - build_graph: Build complete graph from vault
    - get_node: Get a single node by path
    - get_edges: Get edges for a note
    - find_related_notes: Find related notes by traversal
    """

    def __init__(self, vault_path: Path | str):
        """Initialize knowledge graph builder.

        Args:
            vault_path: Path to the Obsidian vault root

        Raises:
            InvalidVaultError: If vault path doesn't exist or isn't a directory
        """
        self._path = Path(vault_path)
        self._parser = NoteParser(self._path)

        if not self._path.exists():
            raise InvalidVaultError(f"Vault path does not exist: {self._path}")
        if not self._path.is_dir():
            raise InvalidVaultError(f"Vault path is not a directory: {self._path}")

    @property
    def vault_path(self) -> Path:
        """Return vault root path."""
        return self._path

    def _is_valid_note(self, path: Path) -> bool:
        """Check if a path is a valid markdown note.

        Args:
            path: Path to check

        Returns:
            True if path is a valid markdown note
        """
        if not path.is_file():
            return False
        if path.suffix.lower() != ".md":
            return False
        if path.name.startswith("."):
            return False
        try:
            relative = path.relative_to(self._path)
            for part in relative.parts:
                if part.startswith("."):
                    return False
        except ValueError:
            return False
        return True

    def _list_all_notes(self) -> list[Path]:
        """List all valid note paths in the vault.

        Returns:
            List of absolute paths to all markdown notes
        """
        notes: list[Path] = []
        import os

        for root, dirs, files in os.walk(self._path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in files:
                file_path = Path(root) / filename
                if self._is_valid_note(file_path):
                    notes.append(file_path)
        return notes

    def _resolve_link_to_path(self, link: str, note_paths: dict[str, str]) -> Optional[str]:
        """Resolve a wikilink to an actual note path.

        Args:
            link: Wikilink target (e.g., "note-name" or "folder/note")
            note_paths: Dict mapping note stems to full paths

        Returns:
            Resolved note path or None if not found
        """
        # Try exact match first
        if link in note_paths:
            return note_paths[link]

        # Try with .md extension
        link_with_ext = f"{link}.md" if not link.endswith(".md") else link
        if link_with_ext in note_paths:
            return note_paths[link_with_ext]

        # Try matching by stem (filename without extension)
        link_stem = Path(link).stem.lower()
        for path_key, full_path in note_paths.items():
            path_stem = Path(path_key).stem.lower()
            if path_stem == link_stem:
                return full_path

        return None

    def build_graph(self) -> GraphData:
        """Build the complete knowledge graph from the vault.

        Returns:
            GraphData with all nodes and edges
        """
        notes = self._list_all_notes()

        # Build a map of note paths for quick lookup
        note_paths: dict[str, str] = {}
        for note_path in notes:
            rel_path = str(note_path.relative_to(self._path))
            note_paths[rel_path] = rel_path
            # Also index by stem for partial matching
            stem = note_path.stem
            note_paths[stem] = rel_path

        # Track connections for each node
        connections: dict[str, set[str]] = {
            rel: set() for rel in note_paths.values() if rel.endswith(".md")
        }

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        for note_path in notes:
            rel_path = str(note_path.relative_to(self._path))

            # Parse note
            try:
                content = note_path.read_text(encoding="utf-8")
                meta = self._parser.parse_note_meta(note_path)
                wikilinks = self._parser.extract_wikilinks(content)
            except Exception:
                continue

            # Create node
            node = GraphNode(
                id=rel_path,
                title=meta.title or note_path.stem,
                path=rel_path,
                tags=meta.tags,
                connections_count=0,  # Will update after processing all edges
            )
            nodes.append(node)

            # Create edges for each wikilink
            for link in wikilinks:
                target_path = self._resolve_link_to_path(link, note_paths)
                if target_path:
                    edge = GraphEdge(
                        source=rel_path,
                        target=target_path,
                        type="wikilink",
                        weight=1.0,
                    )
                    edges.append(edge)

                    # Track connection
                    if rel_path in connections:
                        connections[rel_path].add(target_path)
                    if target_path in connections:
                        connections[target_path].add(rel_path)

        # Update connection counts
        for node in nodes:
            node.connections_count = len(connections.get(node.id, set()))

        return GraphData(nodes=nodes, edges=edges)

    def get_node(self, note_path: str) -> GraphNode:
        """Get a single node by its path.

        Args:
            note_path: Relative path to the note

        Returns:
            GraphNode for the note

        Raises:
            NodeNotFoundError: If note doesn't exist
        """
        full_path = self._path / note_path

        if not full_path.exists():
            raise NodeNotFoundError(f"Node not found: {note_path}")

        # Build graph to get connection count
        graph = self.build_graph()

        for node in graph.nodes:
            if node.id == note_path:
                return node

        raise NodeNotFoundError(f"Node not found: {note_path}")

    def get_edges(self, note_path: str) -> list[GraphEdge]:
        """Get all edges for a note (outgoing).

        Args:
            note_path: Relative path to the note

        Returns:
            List of GraphEdge objects where this note is the source
        """
        graph = self.build_graph()

        return [e for e in graph.edges if e.source == note_path]

    def find_related_notes(self, note_path: str, depth: int) -> list[NoteMeta]:
        """Find notes related to the given note within specified depth.

        Uses BFS traversal to find all notes within 'depth' hops.

        Args:
            note_path: Relative path to the starting note
            depth: Maximum traversal depth (1 = direct connections)

        Returns:
            List of NoteMeta for related notes (excludes the starting note)

        Raises:
            NodeNotFoundError: If the starting note doesn't exist
        """
        full_path = self._path / note_path
        if not full_path.exists():
            raise NodeNotFoundError(f"Node not found: {note_path}")

        graph = self.build_graph()

        # Build adjacency list (both directions)
        adjacency: dict[str, set[str]] = {}
        for edge in graph.edges:
            if edge.source not in adjacency:
                adjacency[edge.source] = set()
            adjacency[edge.source].add(edge.target)

            if edge.target not in adjacency:
                adjacency[edge.target] = set()
            adjacency[edge.target].add(edge.source)

        # BFS traversal
        visited: set[str] = {note_path}
        current_level: set[str] = {note_path}
        related_paths: set[str] = set()

        for _ in range(depth):
            next_level: set[str] = set()
            for node in current_level:
                neighbors = adjacency.get(node, set())
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        related_paths.add(neighbor)
                        next_level.add(neighbor)
            current_level = next_level
            if not current_level:
                break

        # Convert paths to NoteMeta
        result: list[NoteMeta] = []
        for path in related_paths:
            try:
                meta = self._parser.parse_note_meta(self._path / path)
                result.append(meta)
            except Exception:
                continue

        return result
