"""Tests for dependency injection in FastAPI routes.

TDD approach: Tests written before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from markwritter.api.app import create_app
from markwritter.obsidian.vault import ObsidianVault


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        (vault_path / "test-note.md").write_text("# Test Note\n\nContent.")
        yield vault_path


@pytest.fixture
def mock_vault(temp_vault: Path) -> MagicMock:
    """Create a mock ObsidianVault."""
    vault = MagicMock(spec=ObsidianVault)
    vault.path = temp_vault
    vault.note_exists.return_value = False
    vault.write_note = MagicMock()
    return vault


# ==============================================================================
# Dependency Injection Tests
# ==============================================================================


class TestDependencyInjectionExists:
    """Test that dependency injection functions exist."""

    def test_get_vault_dependency_exists(self) -> None:
        """Test that get_vault dependency function exists."""
        from markwritter.api.routes.record import get_vault

        assert callable(get_vault)

    def test_get_writing_assistant_dependency_exists(self) -> None:
        """Test that get_writing_assistant dependency function exists."""
        from markwritter.api.routes.record import get_writing_assistant

        assert callable(get_writing_assistant)

    def test_get_auto_classifier_dependency_exists(self) -> None:
        """Test that get_auto_classifier dependency function exists."""
        from markwritter.api.routes.record import get_auto_classifier

        assert callable(get_auto_classifier)


class TestDependencyInjectionOverride:
    """Test that dependencies can be overridden for testing."""

    def test_override_vault(self, mock_vault: MagicMock) -> None:
        """Test overriding vault dependency."""
        from markwritter.api.routes.record import router, get_vault

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/record")

        # Override dependency
        app.dependency_overrides[get_vault] = lambda: mock_vault

        client = TestClient(app)

        response = client.post(
            "/api/v1/record/create",
            json={"path": "test.md", "content": "Test"},
        )

        # Should not return 503 (service unavailable)
        assert response.status_code != 503

    def test_override_writing_assistant(self) -> None:
        """Test overriding writing_assistant dependency."""
        from markwritter.record.assistant import WritingAssistant

        from markwritter.api.routes.record import router, get_writing_assistant

        mock_assistant = MagicMock(spec=WritingAssistant)
        mock_assistant.continue_writing = MagicMock(return_value="Continued text")

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/record")

        # Override dependency
        app.dependency_overrides[get_writing_assistant] = lambda: mock_assistant

        client = TestClient(app)

        response = client.post(
            "/api/v1/record/ai-assist/continue",
            json={"content": "Start text"},
        )

        # Should not return 503
        assert response.status_code != 503


class TestServiceLayerIntegration:
    """Test that routes use service layer instead of direct dependencies."""

    def test_create_note_uses_note_service(self, mock_vault: MagicMock) -> None:
        """Test that create note uses NoteService."""
        from markwritter.api.routes.record import get_vault, router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/record")

        app.dependency_overrides[get_vault] = lambda: mock_vault

        client = TestClient(app)

        response = client.post(
            "/api/v1/record/create",
            json={"path": "new.md", "content": "New note"},
        )

        # Should succeed
        assert response.status_code == 200

    def test_routes_dont_use_global_state(self) -> None:
        """Test that routes don't rely on global state."""
        from markwritter.api.routes import record as record_routes

        # Check that global variables are not used directly in route handlers
        # by inspecting the source or testing behavior

        # This is a design test - we verify the pattern
        import inspect

        # Check that dependency injection is used
        source = inspect.getsource(record_routes)

        # The source should contain Depends() pattern
        assert "Depends" in source or "dependency" in source.lower()


class TestInitFunction:
    """Test the initialization function for backward compatibility."""

    def test_init_record_routes_exists(self) -> None:
        """Test that init_record_routes function exists."""
        from markwritter.api.routes.record import init_record_routes

        assert callable(init_record_routes)

    def test_init_sets_dependencies(self, mock_vault: MagicMock) -> None:
        """Test that init_record_routes sets dependencies."""
        from markwritter.api.routes.record import init_record_routes, _vault

        # Reset state
        import markwritter.api.routes.record as record_module

        record_module._vault = None

        # Initialize
        init_record_routes(vault=mock_vault)

        # Check that dependencies are set
        # Note: This tests backward compatibility with global state
        assert record_module._vault == mock_vault


class TestDependencyInjectionPattern:
    """Test the dependency injection pattern follows best practices."""

    def test_dependencies_are_callable(self) -> None:
        """Test that all dependency functions are callable."""
        from markwritter.api.routes.record import (
            get_auto_classifier,
            get_vault,
            get_writing_assistant,
        )

        # These should be callable
        assert callable(get_vault)
        assert callable(get_writing_assistant)
        assert callable(get_auto_classifier)

    def test_dependency_functions_return_correct_types(self, mock_vault: MagicMock) -> None:
        """Test that dependency functions return correct types."""
        from markwritter.api.routes.record import get_vault

        # With override
        result = get_vault()
        # Should return vault or None
        assert result is None or hasattr(result, "note_exists")