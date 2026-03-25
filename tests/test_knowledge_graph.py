"""Tests for Knowledge Graph functionality.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from markwritter.obsidian.models import NoteMeta

# ==============================================================================
# Models that will be implemented
# ==============================================================================


class TestGraphModels:
    """Tests for graph data models."""

    def test_graph_node_creation(self) -> None:
        """Test GraphNode model creation."""
        from markwritter.explore.graph import GraphNode

        node = GraphNode(
            id="note1.md",
            title="First Note",
            path="note1.md",
            tags=["python", "testing"],
            connections_count=3,
        )

        assert node.id == "note1.md"
        assert node.title == "First Note"
        assert node.path == "note1.md"
        assert node.tags == ["python", "testing"]
        assert node.connections_count == 3

    def test_graph_edge_creation(self) -> None:
        """Test GraphEdge model creation."""
        from markwritter.explore.graph import GraphEdge

        edge = GraphEdge(
            source="note1.md",
            target="note2.md",
            type="wikilink",
            weight=1.0,
        )

        assert edge.source == "note1.md"
        assert edge.target == "note2.md"
        assert edge.type == "wikilink"
        assert edge.weight == 1.0

    def test_graph_data_creation(self) -> None:
        """Test GraphData model creation."""
        from markwritter.explore.graph import GraphData, GraphEdge, GraphNode

        nodes = [
            GraphNode(id="n1", title="Note 1", path="n1.md", tags=[], connections_count=1),
            GraphNode(id="n2", title="Note 2", path="n2.md", tags=[], connections_count=1),
        ]
        edges = [
            GraphEdge(source="n1.md", target="n2.md", type="wikilink", weight=1.0),
        ]

        graph = GraphData(nodes=nodes, edges=edges)

        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

    def test_graph_data_empty(self) -> None:
        """Test GraphData with no data."""
        from markwritter.explore.graph import GraphData

        graph = GraphData()

        assert graph.nodes == []
        assert graph.edges == []


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def graph_vault() -> Generator[Path, None, None]:
    """Create a temporary vault with interconnected notes for graph testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Central note with many connections
        (vault_path / "central.md").write_text("""---
title: Central Note
tags: [core, important]
---
# Central Note

This is the central hub.

Links to:
- [[note-a]]
- [[note-b]]
- [[projects/project-1|Project 1]]
- [[concepts/design]]
""")

        # Note A
        (vault_path / "note-a.md").write_text("""---
title: Note A
tags: [reference]
---
# Note A

Links back to [[central]].

Also links to [[note-b]].
""")

        # Note B
        (vault_path / "note-b.md").write_text("""---
title: Note B
tags: [reference]
---
# Note B

Links to [[central]] and [[note-a]].
""")

        # Projects subdirectory
        projects_dir = vault_path / "projects"
        projects_dir.mkdir()

        (projects_dir / "project-1.md").write_text("""---
title: Project 1
status: active
---
# Project 1

Main project note.

Related: [[central]], [[concepts/design]]
""")

        # Concepts subdirectory
        concepts_dir = vault_path / "concepts"
        concepts_dir.mkdir()

        (concepts_dir / "design.md").write_text("""---
title: Design Concepts
tags: [design, architecture]
---
# Design Concepts

Core design principles.

Referenced by [[central]] and [[projects/project-1]].
""")

        # Isolated note (no connections)
        (vault_path / "isolated.md").write_text("""---
title: Isolated Note
tags: [draft]
---
# Isolated Note

This note has no connections.
""")

        yield vault_path


# ==============================================================================
# KnowledgeGraph Tests
# ==============================================================================


class TestKnowledgeGraphInit:
    """Tests for KnowledgeGraph initialization."""

    def test_init_with_path(self, graph_vault: Path) -> None:
        """Test initialization with vault path."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)

        assert graph.vault_path == graph_vault

    def test_init_with_string_path(self, graph_vault: Path) -> None:
        """Test initialization with string path."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(str(graph_vault))

        assert graph.vault_path == graph_vault

    def test_init_invalid_path_raises_error(self) -> None:
        """Test that non-existent path raises error."""
        from markwritter.explore.graph import InvalidVaultError, KnowledgeGraph

        with pytest.raises(InvalidVaultError):
            KnowledgeGraph("/non/existent/path")


class TestKnowledgeGraphBuildGraph:
    """Tests for building the complete knowledge graph."""

    def test_build_graph_returns_graph_data(self, graph_vault: Path) -> None:
        """Test that build_graph returns GraphData."""
        from markwritter.explore.graph import GraphData, KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.build_graph()

        assert isinstance(result, GraphData)

    def test_build_graph_includes_all_notes(self, graph_vault: Path) -> None:
        """Test that all notes are included as nodes."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.build_graph()

        node_ids = {n.id for n in result.nodes}

        assert "central.md" in node_ids
        assert "note-a.md" in node_ids
        assert "note-b.md" in node_ids
        assert "projects/project-1.md" in node_ids
        assert "concepts/design.md" in node_ids
        assert "isolated.md" in node_ids

    def test_build_graph_creates_edges(self, graph_vault: Path) -> None:
        """Test that edges are created for wikilinks."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.build_graph()

        # Central has 4 outgoing links
        central_edges = [e for e in result.edges if e.source == "central.md"]
        assert len(central_edges) == 4

    def test_build_graph_edge_targets(self, graph_vault: Path) -> None:
        """Test that edges have correct targets."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.build_graph()

        # Find edges from central
        central_targets = {e.target for e in result.edges if e.source == "central.md"}

        # Links are resolved to actual note paths
        assert "note-a.md" in central_targets
        assert "note-b.md" in central_targets

    def test_build_graph_node_has_correct_connections_count(self, graph_vault: Path) -> None:
        """Test that nodes have correct connection counts."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.build_graph()

        # Find central node
        central_node = next(n for n in result.nodes if n.id == "central.md")

        # Central has 4 outgoing + 3 incoming (from note-a, note-b, project-1)
        assert central_node.connections_count >= 4

    def test_build_graph_isolated_node(self, graph_vault: Path) -> None:
        """Test that isolated nodes have zero connections."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.build_graph()

        isolated_node = next(n for n in result.nodes if n.id == "isolated.md")

        assert isolated_node.connections_count == 0

    def test_build_graph_empty_vault(self, tmp_path: Path) -> None:
        """Test building graph for empty vault."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(tmp_path)
        result = graph.build_graph()

        assert result.nodes == []
        assert result.edges == []


class TestKnowledgeGraphGetNode:
    """Tests for getting a single node."""

    def test_get_node_returns_graph_node(self, graph_vault: Path) -> None:
        """Test that get_node returns GraphNode."""
        from markwritter.explore.graph import GraphNode, KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.get_node("central.md")

        assert isinstance(result, GraphNode)
        assert result.id == "central.md"
        assert result.title == "Central Note"

    def test_get_node_with_tags(self, graph_vault: Path) -> None:
        """Test that node includes tags."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.get_node("central.md")

        assert "core" in result.tags
        assert "important" in result.tags

    def test_get_node_not_found_raises_error(self, graph_vault: Path) -> None:
        """Test that non-existent node raises error."""
        from markwritter.explore.graph import KnowledgeGraph, NodeNotFoundError

        graph = KnowledgeGraph(graph_vault)

        with pytest.raises(NodeNotFoundError):
            graph.get_node("nonexistent.md")

    def test_get_node_in_subdirectory(self, graph_vault: Path) -> None:
        """Test getting node from subdirectory."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.get_node("projects/project-1.md")

        assert result.id == "projects/project-1.md"
        assert result.title == "Project 1"


class TestKnowledgeGraphGetEdges:
    """Tests for getting edges for a node."""

    def test_get_edges_returns_list(self, graph_vault: Path) -> None:
        """Test that get_edges returns list of GraphEdge."""
        from markwritter.explore.graph import GraphEdge, KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.get_edges("central.md")

        assert isinstance(result, list)
        assert all(isinstance(e, GraphEdge) for e in result)

    def test_get_edges_outgoing(self, graph_vault: Path) -> None:
        """Test getting outgoing edges."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.get_edges("central.md")

        sources = {e.source for e in result}
        assert sources == {"central.md"}

    def test_get_edges_incoming(self, graph_vault: Path) -> None:
        """Test that incoming edges are included when requested."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)

        # Get edges where central is the target (incoming)
        all_edges = graph.build_graph().edges
        incoming = [e for e in all_edges if e.target == "central.md"]

        assert len(incoming) >= 2  # At least from note-a and note-b

    def test_get_edges_isolated_node(self, graph_vault: Path) -> None:
        """Test getting edges for isolated node."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.get_edges("isolated.md")

        assert result == []


class TestKnowledgeGraphFindRelatedNotes:
    """Tests for finding related notes."""

    def test_find_related_returns_note_meta_list(self, graph_vault: Path) -> None:
        """Test that find_related_notes returns list of NoteMeta."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.find_related_notes("central.md", depth=1)

        assert isinstance(result, list)
        assert all(isinstance(n, NoteMeta) for n in result)

    def test_find_related_depth_1(self, graph_vault: Path) -> None:
        """Test finding directly related notes (depth=1)."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.find_related_notes("central.md", depth=1)

        paths = {n.path for n in result}

        # Directly linked notes
        assert "note-a.md" in paths
        assert "note-b.md" in paths
        assert "projects/project-1.md" in paths
        assert "concepts/design.md" in paths

    def test_find_related_depth_2(self, graph_vault: Path) -> None:
        """Test finding notes within 2 hops (depth=2)."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.find_related_notes("central.md", depth=2)

        paths = {n.path for n in result}

        # Depth 1 notes
        assert "note-a.md" in paths
        assert "note-b.md" in paths

        # Depth 2 (notes linked by note-a, note-b, etc.)
        # note-a links to note-b, note-b links back to note-a
        # So these are still included
        assert len(result) >= 4

    def test_find_related_excludes_self(self, graph_vault: Path) -> None:
        """Test that the note itself is not included in results."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.find_related_notes("central.md", depth=1)

        paths = {n.path for n in result}
        assert "central.md" not in paths

    def test_find_related_isolated_node(self, graph_vault: Path) -> None:
        """Test finding related notes for isolated node."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)
        result = graph.find_related_notes("isolated.md", depth=1)

        assert result == []

    def test_find_related_node_not_found(self, graph_vault: Path) -> None:
        """Test finding related notes for non-existent node."""
        from markwritter.explore.graph import KnowledgeGraph, NodeNotFoundError

        graph = KnowledgeGraph(graph_vault)

        with pytest.raises(NodeNotFoundError):
            graph.find_related_notes("nonexistent.md", depth=1)

    def test_find_related_respects_depth(self, graph_vault: Path) -> None:
        """Test that depth parameter limits traversal."""
        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(graph_vault)

        depth_1 = graph.find_related_notes("central.md", depth=1)
        depth_2 = graph.find_related_notes("central.md", depth=2)

        # Depth 2 should have at least as many results as depth 1
        assert len(depth_2) >= len(depth_1)


class TestKnowledgeGraphEdgeCases:
    """Tests for edge cases and error handling."""

    def test_circular_links(self, tmp_path: Path) -> None:
        """Test handling circular link patterns."""
        # Create circular links: A -> B -> C -> A
        (tmp_path / "a.md").write_text("[[b]]")
        (tmp_path / "b.md").write_text("[[c]]")
        (tmp_path / "c.md").write_text("[[a]]")

        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(tmp_path)
        result = graph.build_graph()

        # Should not hang and should detect all edges
        assert len(result.nodes) == 3
        assert len(result.edges) == 3

    def test_self_referencing_note(self, tmp_path: Path) -> None:
        """Test handling notes that link to themselves."""
        (tmp_path / "self.md").write_text("---\ntitle: Self Note\n---\n[[self]]")

        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(tmp_path)
        result = graph.build_graph()

        # Self-referencing should be included
        assert len(result.nodes) == 1
        # Self-edges may or may not be included - just verify no crash

    def test_broken_wikilink(self, tmp_path: Path) -> None:
        """Test handling wikilinks to non-existent notes."""
        (tmp_path / "broken.md").write_text("[[nonexistent-note]]")

        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(tmp_path)
        result = graph.build_graph()

        # Should include the note, but edge target may be unresolved
        assert len(result.nodes) == 1

    def test_large_graph_performance(self, tmp_path: Path) -> None:
        """Test building graph with many nodes."""
        import time

        # Create 100 interconnected notes
        for i in range(100):
            content = f"---\ntitle: Note {i}\n---\n"
            # Each note links to next 3 notes
            for j in range(i + 1, min(i + 4, 100)):
                content += f"[[note-{j}]]\n"
            (tmp_path / f"note-{i}.md").write_text(content)

        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(tmp_path)

        start = time.time()
        result = graph.build_graph()
        elapsed = time.time() - start

        # Should complete within reasonable time (< 5 seconds)
        assert elapsed < 5.0
        assert len(result.nodes) == 100

    def test_unicode_in_notes(self, tmp_path: Path) -> None:
        """Test handling unicode in note content."""
        (tmp_path / "unicode.md").write_text("""---
title: Unicode Test
tags: [emoji, i18n]
---
# Unicode Test

Content with emoji: content

Links: [[日本語]], [[emoji-world]]
""")

        from markwritter.explore.graph import KnowledgeGraph

        graph = KnowledgeGraph(tmp_path)
        result = graph.build_graph()

        assert len(result.nodes) == 1
        assert result.nodes[0].title == "Unicode Test"
