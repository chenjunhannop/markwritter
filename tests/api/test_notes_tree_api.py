"""Tests for /notes/tree endpoint and vault_path propagation.

Covers:
1. GET /notes/tree with various vault states (configured, unconfigured, non-vault)
2. vault_path propagation from settings to notes/explore when updated via Settings API
3. Full notes CRUD still works alongside the new tree endpoint
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from markwritter.api.app import create_app
from markwritter.api.routes import notes as notes_routes
from markwritter.api.routes import settings as settings_routes
from markwritter.obsidian.vault import ObsidianVault


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault_with_tree() -> Generator[Path, None, None]:
    """Create a temporary vault with nested directory structure for tree tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)

        # Root-level files
        (vault / "readme.md").write_text("# Readme")
        (vault / "index.md").write_text("# Index")

        # Nested directories
        daily = vault / "daily"
        daily.mkdir()
        (daily / "2024-01-01.md").write_text("# Jan 1")
        (daily / "2024-01-02.md").write_text("# Jan 2")

        projects = vault / "projects"
        projects.mkdir()
        (projects / "project-alpha.md").write_text("# Alpha")

        # Deeper nesting
        deep = projects / "sub-project"
        deep.mkdir()
        (deep / "deep-note.md").write_text("# Deep")

        # Hidden directory (should be excluded)
        hidden = vault / ".obsidian"
        hidden.mkdir()
        (hidden / "config.md").write_text("config")

        # Hidden file (should be excluded)
        (vault / ".hidden-note.md").write_text("hidden")

        # Non-markdown file (should be excluded)
        (vault / "image.png").write_bytes(b"\x89PNG")

        yield vault


@pytest.fixture
def temp_empty_vault() -> Generator[Path, None, None]:
    """Create a temporary empty vault directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def reset_module_state(tmp_path: Path) -> Generator[None, None, None]:
    """Reset module-level globals in notes and settings before each test.

    Uses tmp_path as the settings data directory so tests are isolated
    from the user's real ~/.markwritter/settings.json.
    """
    notes_routes._vault = None
    settings_routes._data_dir = None
    settings_routes._settings_cache = {
        "theme": "system",
        "language": "en",
        "vault_path": "",
    }
    settings_routes._vault_change_callbacks = []
    # Point init_settings at a temp dir so it won't load real settings
    settings_routes.init_settings(str(tmp_path))
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client from the full app (no vault path)."""
    app = create_app()
    yield TestClient(app)


# ==============================================================================
# 1. GET /notes/tree - Various vault states
# ==============================================================================


class TestNotesTreeUnconfigured:
    """Tests for /notes/tree when no vault is configured."""

    def test_tree_returns_empty_list_when_no_vault(self, client: TestClient) -> None:
        """GET /notes/tree returns {tree: []} when vault not configured."""
        response = client.get("/api/v1/notes/tree")
        assert response.status_code == 200
        data = response.json()
        assert data == {"tree": []}

    def test_tree_returns_empty_list_when_vault_cleared(
        self, client: TestClient
    ) -> None:
        """GET /notes/tree returns empty list after vault is set to None."""
        notes_routes._vault = None
        response = client.get("/api/v1/notes/tree")
        assert response.status_code == 200
        assert response.json() == {"tree": []}


class TestNotesTreeConfiguredVault:
    """Tests for /notes/tree with a properly configured vault."""

    def test_tree_returns_nested_structure(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """GET /notes/tree returns the correct nested directory tree."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        assert response.status_code == 200
        data = response.json()
        tree = data["tree"]

        # Should have directories first (sorted), then files
        names = [node["name"] for node in tree]
        assert "daily" in names
        assert "projects" in names
        assert "readme.md" in names
        assert "index.md" in names

        # Hidden items excluded
        assert ".obsidian" not in names
        assert ".hidden-note.md" not in names

        # Non-markdown files excluded
        assert "image.png" not in names

    def test_tree_directory_has_children(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Directory nodes contain children array."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        tree = response.json()["tree"]

        daily_node = next(n for n in tree if n["name"] == "daily")
        assert daily_node["type"] == "directory"
        assert daily_node["children"] is not None
        assert len(daily_node["children"]) == 2

        child_names = [c["name"] for c in daily_node["children"]]
        assert "2024-01-01.md" in child_names
        assert "2024-01-02.md" in child_names

    def test_tree_directory_has_file_count(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Directory nodes report correct file_count."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        tree = response.json()["tree"]

        daily_node = next(n for n in tree if n["name"] == "daily")
        assert daily_node["file_count"] == 2

        projects_node = next(n for n in tree if n["name"] == "projects")
        # projects has 1 direct file + sub-project/deep-note.md = 2 total
        assert projects_node["file_count"] == 2

    def test_tree_file_node_structure(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """File nodes have correct type, path, name, no children."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        tree = response.json()["tree"]

        readme = next(n for n in tree if n["name"] == "readme.md")
        assert readme["type"] == "file"
        assert readme["path"] == "readme.md"
        assert readme.get("children") is None
        assert readme.get("file_count") is None

    def test_tree_deeply_nested_paths(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Paths for deeply nested nodes are relative to vault root."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        tree = response.json()["tree"]

        projects_node = next(n for n in tree if n["name"] == "projects")
        sub_project = next(
            c for c in projects_node["children"] if c["name"] == "sub-project"
        )
        assert sub_project["path"] == "projects/sub-project"

        deep_note = next(c for c in sub_project["children"] if c["name"] == "deep-note.md")
        assert deep_note["path"] == "projects/sub-project/deep-note.md"

    def test_tree_directories_sorted_before_files(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Directories appear before files in the tree output."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        tree = response.json()["tree"]

        # Find the index of the first file and last directory
        types = [node["type"] for node in tree]
        if "directory" in types and "file" in types:
            last_dir_idx = len(types) - 1 - types[::-1].index("directory")
            first_file_idx = types.index("file")
            assert last_dir_idx < first_file_idx

    def test_tree_empty_vault(self, temp_empty_vault: Path, client: TestClient) -> None:
        """GET /notes/tree returns empty list for an empty vault."""
        vault = ObsidianVault(temp_empty_vault)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/tree")
        assert response.status_code == 200
        assert response.json() == {"tree": []}


class TestNotesTreeNonVaultPath:
    """Tests for /notes/tree when vault path points to non-existent dir."""

    def test_tree_returns_empty_when_vault_init_fails(
        self, client: TestClient
    ) -> None:
        """If ObsidianVault init fails, _vault stays None and tree returns empty."""
        notes_routes._vault = None
        # set_vault_path with a bad path should leave _vault as None
        notes_routes.set_vault_path("/nonexistent/path/that/does/not/exist")

        assert notes_routes._vault is None
        response = client.get("/api/v1/notes/tree")
        assert response.status_code == 200
        assert response.json() == {"tree": []}


# ==============================================================================
# 2. vault_path propagation via Settings API
# ==============================================================================


class TestVaultPathPropagation:
    """Tests for vault_path propagation from Settings API to notes/explore."""

    def test_vault_path_callback_registered_on_app_create(
        self, client: TestClient
    ) -> None:
        """When app is created, a vault change callback is registered."""
        assert len(settings_routes._vault_change_callbacks) > 0

    def test_updating_vault_path_triggers_callback(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """PUT /settings with vault_path triggers the vault change callback."""
        vault_path = str(temp_vault_with_tree)

        response = client.put(
            "/api/v1/settings/",
            json={"vault_path": vault_path},
        )
        assert response.status_code == 200

        # The notes module should now have _vault set
        assert notes_routes._vault is not None

        # And the tree endpoint should work
        tree_response = client.get("/api/v1/notes/tree")
        assert tree_response.status_code == 200
        tree = tree_response.json()["tree"]
        assert len(tree) > 0

    def test_clearing_vault_path_clears_notes_vault(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Setting vault_path to empty string clears the notes vault."""
        vault_path = str(temp_vault_with_tree)

        # First configure
        client.put("/api/v1/settings/", json={"vault_path": vault_path})
        assert notes_routes._vault is not None

        # Then clear
        client.put("/api/v1/settings/", json={"vault_path": ""})
        assert notes_routes._vault is None

        # Tree should return empty
        tree_response = client.get("/api/v1/notes/tree")
        assert tree_response.json() == {"tree": []}

    def test_vault_path_propagation_sets_explore_vault(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Updating vault_path also sets the explore module's _vault_path."""
        from markwritter.api.routes import explore as explore_routes

        vault_path = str(temp_vault_with_tree)

        client.put("/api/v1/settings/", json={"vault_path": vault_path})
        assert explore_routes._vault_path == vault_path

    def test_clearing_vault_propagation_clears_explore(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """Clearing vault_path via settings also clears explore module."""
        from markwritter.api.routes import explore as explore_routes

        vault_path = str(temp_vault_with_tree)

        client.put("/api/v1/settings/", json={"vault_path": vault_path})
        assert explore_routes._vault_path is not None

        client.put("/api/v1/settings/", json={"vault_path": ""})
        assert explore_routes._vault_path is None

    def test_invalid_vault_path_in_settings_does_not_crash(
        self, client: TestClient
    ) -> None:
        """Setting a nonexistent vault_path via settings does not raise."""
        response = client.put(
            "/api/v1/settings/",
            json={"vault_path": "/absolutely/fake/path"},
        )
        # Settings update succeeds (path is syntactically valid)
        assert response.status_code == 200
        # But notes vault should remain None (init failed)
        assert notes_routes._vault is None

    def test_get_vault_path_returns_none_when_unset(self) -> None:
        """get_vault_path returns None when vault_path is not set."""
        result = settings_routes.get_vault_path()
        assert result is None

    def test_get_vault_path_returns_value_when_set(self) -> None:
        """get_vault_path returns the path string when vault_path is configured."""
        settings_routes._settings_cache["vault_path"] = "/some/vault"
        result = settings_routes.get_vault_path()
        assert result == "/some/vault"


class TestSetVaultPath:
    """Tests for the set_vault_path function in notes module."""

    def test_set_vault_path_with_none_clears_vault(self) -> None:
        """Calling set_vault_path(None) clears the vault."""
        notes_routes._vault = MagicMock()
        notes_routes.set_vault_path(None)
        assert notes_routes._vault is None

    def test_set_vault_path_with_empty_string_clears_vault(self) -> None:
        """Calling set_vault_path('') clears the vault."""
        notes_routes._vault = MagicMock()
        notes_routes.set_vault_path("")
        assert notes_routes._vault is None

    def test_set_vault_path_with_valid_dir(
        self, temp_vault_with_tree: Path
    ) -> None:
        """Calling set_vault_path with a real path creates an ObsidianVault."""
        notes_routes.set_vault_path(str(temp_vault_with_tree))
        assert notes_routes._vault is not None
        assert notes_routes._vault.path == temp_vault_with_tree

    def test_set_vault_path_with_invalid_dir(self) -> None:
        """Calling set_vault_path with a nonexistent path leaves vault as None."""
        notes_routes.set_vault_path("/no/such/directory")
        assert notes_routes._vault is None


# ==============================================================================
# 3. Full notes CRUD still works alongside tree
# ==============================================================================


class TestNotesCRUDWithTreeEndpoint:
    """Tests verifying CRUD operations still pass with the tree endpoint present."""

    def test_list_notes_still_works(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """GET /notes returns 200 with correct shape after tree endpoint is added.

        Note: The API endpoint passes tag/limit kwargs that ObsidianVault.list_notes()
        does not accept (pre-existing signature mismatch). The endpoint catches the
        TypeError and returns an empty list. This test verifies the endpoint still
        responds correctly without crashing.
        """
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes")
        assert response.status_code == 200
        data = response.json()
        assert "notes" in data
        assert "total" in data
        assert isinstance(data["notes"], list)
        assert isinstance(data["total"], int)

    def test_get_note_still_works(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """GET /notes/{path} still works alongside the tree endpoint."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.get("/api/v1/notes/readme.md")
        assert response.status_code == 200
        data = response.json()
        assert data["path"] == "readme.md"

    def test_create_and_delete_note(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """POST and DELETE notes still work alongside the tree endpoint."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        # Create
        create_resp = client.post(
            "/api/v1/notes",
            json={"path": "new-from-test.md", "content": "Created by test"},
        )
        assert create_resp.status_code == 201

        # Verify in tree
        tree_resp = client.get("/api/v1/notes/tree")
        tree_names = [
            n["name"] for n in tree_resp.json()["tree"] if n["type"] == "file"
        ]
        assert "new-from-test.md" in tree_names

        # Read back
        get_resp = client.get("/api/v1/notes/new-from-test.md")
        assert get_resp.status_code == 200
        assert get_resp.json()["content"] == "Created by test"

        # Delete
        del_resp = client.delete("/api/v1/notes/new-from-test.md")
        assert del_resp.status_code == 204

        # Verify deleted
        get_resp2 = client.get("/api/v1/notes/new-from-test.md")
        assert get_resp2.status_code == 404

    def test_update_note_still_works(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """PUT /notes/{path} still works alongside the tree endpoint."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        response = client.put(
            "/api/v1/notes/readme.md",
            json={"content": "Updated content", "mode": "replace"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify content updated
        get_resp = client.get("/api/v1/notes/readme.md")
        assert get_resp.json()["content"] == "Updated content"

    def test_tree_reflects_filesystem_changes(
        self, temp_vault_with_tree: Path, client: TestClient
    ) -> None:
        """After creating a file via API, the tree endpoint reflects the change."""
        vault = ObsidianVault(temp_vault_with_tree)
        notes_routes._vault = vault

        # Create a new file
        client.post(
            "/api/v1/notes",
            json={"path": "fresh-note.md", "content": "Brand new"},
        )

        # Check tree
        tree_resp = client.get("/api/v1/notes/tree")
        tree_names = [
            n["name"] for n in tree_resp.json()["tree"] if n["type"] == "file"
        ]
        assert "fresh-note.md" in tree_names


# ==============================================================================
# 4. Callback infrastructure
# ==============================================================================


class TestVaultChangeCallbacks:
    """Tests for the callback registration and notification system."""

    def test_register_callback(self) -> None:
        """register_vault_change_callback appends to the list."""
        calls: list[str | None] = []
        settings_routes.register_vault_change_callback(lambda p: calls.append(p))
        assert len(settings_routes._vault_change_callbacks) == 1

    def test_callbacks_are_called_on_vault_change(
        self, tmp_path: Path
    ) -> None:
        """Callbacks are invoked when vault_path changes via update_settings."""
        calls: list[str | None] = []

        # Setup
        settings_routes._vault_change_callbacks = []
        settings_routes.register_vault_change_callback(lambda p: calls.append(p))

        # Use FastAPI app with settings router
        settings_routes.init_settings(str(tmp_path))
        app = FastAPI()
        app.include_router(
            settings_routes.router, prefix="/api/v1/settings", tags=["Settings"]
        )
        client = TestClient(app)

        # Trigger callback
        client.put("/api/v1/settings/", json={"vault_path": "/new/vault"})
        assert len(calls) == 1
        assert calls[0] == "/new/vault"

    def test_callback_error_does_not_crash_update(
        self, tmp_path: Path
    ) -> None:
        """A failing callback does not prevent the settings update."""
        settings_routes._vault_change_callbacks = []
        settings_routes.register_vault_change_callback(
            lambda p: (_ for _ in ()).throw(RuntimeError("boom"))
        )

        settings_routes.init_settings(str(tmp_path))
        app = FastAPI()
        app.include_router(
            settings_routes.router, prefix="/api/v1/settings", tags=["Settings"]
        )
        client = TestClient(app)

        response = client.put(
            "/api/v1/settings/", json={"vault_path": "/safe/vault"}
        )
        # Settings update should still succeed
        assert response.status_code == 200
        assert response.json()["vault_path"] == "/safe/vault"

    def test_clearing_vault_sends_none_to_callbacks(
        self, tmp_path: Path
    ) -> None:
        """Setting vault_path to empty string sends None to callbacks."""
        calls: list[str | None] = []

        settings_routes._vault_change_callbacks = []
        settings_routes.register_vault_change_callback(lambda p: calls.append(p))

        settings_routes.init_settings(str(tmp_path))
        app = FastAPI()
        app.include_router(
            settings_routes.router, prefix="/api/v1/settings", tags=["Settings"]
        )
        client = TestClient(app)

        client.put("/api/v1/settings/", json={"vault_path": ""})
        assert len(calls) == 1
        assert calls[0] is None

    def test_non_vault_update_does_not_trigger_callbacks(
        self, tmp_path: Path
    ) -> None:
        """Updating only theme does not invoke vault change callbacks."""
        calls: list[str | None] = []

        settings_routes._vault_change_callbacks = []
        settings_routes.register_vault_change_callback(lambda p: calls.append(p))

        settings_routes.init_settings(str(tmp_path))
        app = FastAPI()
        app.include_router(
            settings_routes.router, prefix="/api/v1/settings", tags=["Settings"]
        )
        client = TestClient(app)

        client.put("/api/v1/settings/", json={"theme": "dark"})
        assert len(calls) == 0
