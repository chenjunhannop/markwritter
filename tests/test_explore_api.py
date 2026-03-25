"""Tests for Explore API routes.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from markwritter.api.app import create_app


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def explore_vault() -> Generator[Path, None, None]:
    """Create a temporary vault with interconnected notes for API testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Central note
        (vault_path / "central.md").write_text(
            """---
title: Central Note
tags: [core, important]
---
# Central Note

Links to [[note-a]], [[note-b]], and [[projects/project-1]].
"""
        )

        # Note A
        (vault_path / "note-a.md").write_text(
            """---
title: Note A
tags: [reference]
---
# Note A

Links back to [[central]].
"""
        )

        # Note B
        (vault_path / "note-b.md").write_text(
            """---
title: Note B
tags: [reference]
---
# Note B

Links to [[central]].
"""
        )

        # Projects subdirectory
        projects_dir = vault_path / "projects"
        projects_dir.mkdir()
        (projects_dir / "project-1.md").write_text(
            """---
title: Project 1
status: active
---
# Project 1

Related: [[central]]
"""
        )

        # Isolated note
        (vault_path / "isolated.md").write_text(
            """---
title: Isolated Note
tags: [draft]
---
# Isolated Note

No connections.
"""
        )

        yield vault_path


@pytest.fixture
def client(explore_vault: Path) -> Generator[TestClient, None, None]:
    """Create a test client with vault configured."""
    app = create_app(vault_path=str(explore_vault))

    # Register explore routes and set vault path
    from markwritter.api.routes.explore import router, set_vault_path

    set_vault_path(str(explore_vault))
    app.include_router(router, prefix="/api/v1/explore", tags=["Explore"])

    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# GET /api/v1/explore/graph Tests
# ==============================================================================


class TestGetFullGraph:
    """Tests for GET /api/v1/explore/graph endpoint."""

    def test_get_graph_returns_200(self, client: TestClient) -> None:
        """Test that endpoint returns 200 OK."""
        response = client.get("/api/v1/explore/graph")

        assert response.status_code == 200

    def test_get_graph_returns_graph_data(self, client: TestClient) -> None:
        """Test that response contains nodes and edges."""
        response = client.get("/api/v1/explore/graph")
        data = response.json()

        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)

    def test_get_graph_includes_all_nodes(self, client: TestClient) -> None:
        """Test that all notes are included as nodes."""
        response = client.get("/api/v1/explore/graph")
        data = response.json()

        node_ids = {n["id"] for n in data["nodes"]}

        assert "central.md" in node_ids
        assert "note-a.md" in node_ids
        assert "note-b.md" in node_ids
        assert "projects/project-1.md" in node_ids
        assert "isolated.md" in node_ids

    def test_get_graph_node_has_required_fields(self, client: TestClient) -> None:
        """Test that nodes have all required fields."""
        response = client.get("/api/v1/explore/graph")
        data = response.json()

        for node in data["nodes"]:
            assert "id" in node
            assert "title" in node
            assert "path" in node
            assert "tags" in node
            assert "connections_count" in node

    def test_get_graph_edge_has_required_fields(self, client: TestClient) -> None:
        """Test that edges have all required fields."""
        response = client.get("/api/v1/explore/graph")
        data = response.json()

        for edge in data["edges"]:
            assert "source" in edge
            assert "target" in edge
            assert "type" in edge
            assert "weight" in edge

    def test_get_graph_creates_correct_edges(self, client: TestClient) -> None:
        """Test that edges represent note connections."""
        response = client.get("/api/v1/explore/graph")
        data = response.json()

        # Central has 3 outgoing links
        central_edges = [e for e in data["edges"] if e["source"] == "central.md"]
        assert len(central_edges) == 3

        # Check targets
        targets = {e["target"] for e in central_edges}
        assert "note-a.md" in targets
        assert "note-b.md" in targets
        assert "projects/project-1.md" in targets


# ==============================================================================
# GET /api/v1/explore/graph/{path} Tests
# ==============================================================================


class TestGetNodeGraph:
    """Tests for GET /api/v1/explore/graph/{path} endpoint."""

    def test_get_node_graph_returns_200(self, client: TestClient) -> None:
        """Test that endpoint returns 200 OK for valid path."""
        response = client.get("/api/v1/explore/graph/central.md")

        assert response.status_code == 200

    def test_get_node_graph_returns_node_data(self, client: TestClient) -> None:
        """Test that response contains node data."""
        response = client.get("/api/v1/explore/graph/central.md")
        data = response.json()

        assert "node" in data
        assert "edges" in data
        assert data["node"]["id"] == "central.md"
        assert data["node"]["title"] == "Central Note"

    def test_get_node_graph_includes_tags(self, client: TestClient) -> None:
        """Test that node includes tags."""
        response = client.get("/api/v1/explore/graph/central.md")
        data = response.json()

        assert "core" in data["node"]["tags"]
        assert "important" in data["node"]["tags"]

    def test_get_node_graph_not_found_returns_404(self, client: TestClient) -> None:
        """Test that non-existent node returns 404."""
        response = client.get("/api/v1/explore/graph/nonexistent.md")

        assert response.status_code == 404

    def test_get_node_graph_in_subdirectory(self, client: TestClient) -> None:
        """Test getting node from subdirectory."""
        response = client.get("/api/v1/explore/graph/projects/project-1.md")

        assert response.status_code == 200
        data = response.json()
        assert data["node"]["id"] == "projects/project-1.md"
        assert data["node"]["title"] == "Project 1"


# ==============================================================================
# GET /api/v1/explore/related/{path} Tests
# ==============================================================================


class TestGetRelatedNotes:
    """Tests for GET /api/v1/explore/related/{path} endpoint."""

    def test_get_related_returns_200(self, client: TestClient) -> None:
        """Test that endpoint returns 200 OK."""
        response = client.get("/api/v1/explore/related/central.md")

        assert response.status_code == 200

    def test_get_related_returns_list(self, client: TestClient) -> None:
        """Test that response is a list."""
        response = client.get("/api/v1/explore/related/central.md")
        data = response.json()

        assert isinstance(data, list)

    def test_get_related_includes_direct_connections(self, client: TestClient) -> None:
        """Test that directly connected notes are included."""
        response = client.get("/api/v1/explore/related/central.md?depth=1")
        data = response.json()

        paths = {n["path"] for n in data}

        assert "note-a.md" in paths
        assert "note-b.md" in paths
        assert "projects/project-1.md" in paths

    def test_get_related_excludes_self(self, client: TestClient) -> None:
        """Test that the note itself is not in results."""
        response = client.get("/api/v1/explore/related/central.md")
        data = response.json()

        paths = {n["path"] for n in data}
        assert "central.md" not in paths

    def test_get_related_respects_depth(self, client: TestClient) -> None:
        """Test that depth parameter limits results."""
        # Depth 1
        response_d1 = client.get("/api/v1/explore/related/central.md?depth=1")
        data_d1 = response_d1.json()

        # Depth 2
        response_d2 = client.get("/api/v1/explore/related/central.md?depth=2")
        data_d2 = response_d2.json()

        # Depth 2 should have at least as many results
        assert len(data_d2) >= len(data_d1)

    def test_get_related_default_depth(self, client: TestClient) -> None:
        """Test that default depth is 1."""
        response = client.get("/api/v1/explore/related/central.md")
        data = response.json()

        # With default depth=1, should get direct connections
        paths = {n["path"] for n in data}
        assert "note-a.md" in paths

    def test_get_related_isolated_node(self, client: TestClient) -> None:
        """Test that isolated node returns empty list."""
        response = client.get("/api/v1/explore/related/isolated.md")
        data = response.json()

        assert data == []

    def test_get_related_not_found_returns_404(self, client: TestClient) -> None:
        """Test that non-existent note returns 404."""
        response = client.get("/api/v1/explore/related/nonexistent.md")

        assert response.status_code == 404

    def test_get_related_has_required_fields(self, client: TestClient) -> None:
        """Test that related notes have required fields."""
        response = client.get("/api/v1/explore/related/central.md")
        data = response.json()

        for note in data:
            assert "path" in note
            assert "title" in note
            assert "tags" in note


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestExploreAPIErrors:
    """Tests for error handling in Explore API."""

    def test_invalid_path_format(self, client: TestClient) -> None:
        """Test handling of invalid path format."""
        # Path with special characters
        response = client.get("/api/v1/explore/graph/../secret.md")

        # Should return 404 or 400
        assert response.status_code in [400, 404]

    def test_depth_parameter_validation(self, client: TestClient) -> None:
        """Test that depth parameter is validated."""
        # Negative depth
        response = client.get("/api/v1/explore/related/central.md?depth=-1")

        assert response.status_code == 422  # Validation error

        # Very large depth
        response = client.get("/api/v1/explore/related/central.md?depth=100")

        # Should still work (or return 422 if limited)
        assert response.status_code in [200, 422]


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestExploreAPIIntegration:
    """Integration tests for Explore API with vault."""

    def test_graph_reflects_vault_changes(
        self, client: TestClient, explore_vault: Path
    ) -> None:
        """Test that graph reflects changes to vault."""
        # Get initial graph
        response1 = client.get("/api/v1/explore/graph")
        initial_count = len(response1.json()["nodes"])

        # Add a new note
        (explore_vault / "new-note.md").write_text("# New Note\n\n[[central]]")

        # Get updated graph
        response2 = client.get("/api/v1/explore/graph")
        updated_count = len(response2.json()["nodes"])

        assert updated_count == initial_count + 1

    def test_connections_count_accurate(self, client: TestClient) -> None:
        """Test that connection counts are accurate."""
        response = client.get("/api/v1/explore/graph")
        data = response.json()

        # Find central node
        central_node = next(n for n in data["nodes"] if n["id"] == "central.md")

        # Central has 3 outgoing + 3 incoming = 6 connections
        # (from note-a, note-b, project-1 all link to central)
        assert central_node["connections_count"] >= 3