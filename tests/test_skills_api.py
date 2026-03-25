"""Tests for Skills API."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestSkillsAPI:
    """Test Skills API endpoints."""

    def test_list_skills_returns_list(self):
        """Test GET /api/skills returns a list."""
        from markwritter.api.app import get_app

        # Mock the framework to avoid loading real skills
        with patch("markwritter.api.routes.skills.get_framework") as mock_get_framework:
            mock_framework = MagicMock()
            mock_framework.registry.list_all.return_value = []
            mock_get_framework.return_value = mock_framework

            app = get_app()
            client = TestClient(app)
            response = client.get("/api/skills/")
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    def test_get_skill_not_found(self):
        """Test GET /api/skills/{name} with non-existent skill."""
        from markwritter.api.app import get_app

        with patch("markwritter.api.routes.skills.get_framework") as mock_get_framework:
            mock_framework = MagicMock()
            mock_framework.registry.get.return_value = None
            mock_get_framework.return_value = mock_framework

            app = get_app()
            client = TestClient(app)
            response = client.get("/api/skills/nonexistent-skill-xyz")
            assert response.status_code == 404

    def test_get_skill_found(self):
        """Test GET /api/skills/{name} with existing skill."""
        from markwritter.api.app import get_app
        from markwritter.models import SkillDefinition, SkillExecution, SkillOutput

        mock_skill = SkillDefinition(
            name="test-skill",
            description="A test skill",
            version="1.0.0",
            execution=SkillExecution(command="echo", script="test.sh"),
            output=SkillOutput(),
        )

        with patch("markwritter.api.routes.skills.get_framework") as mock_get_framework:
            mock_framework = MagicMock()
            mock_framework.registry.get.return_value = mock_skill
            mock_get_framework.return_value = mock_framework

            app = get_app()
            client = TestClient(app)
            response = client.get("/api/skills/test-skill")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "test-skill"
            assert data["description"] == "A test skill"
