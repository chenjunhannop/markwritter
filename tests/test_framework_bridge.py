"""Tests for framework bridge service."""

from unittest.mock import MagicMock, patch

from markwritter.api.services.framework_bridge import get_framework, reset_framework


class TestFrameworkBridge:
    """Test framework bridge service."""

    def setup_method(self):
        """Reset framework before each test."""
        reset_framework()

    def teardown_method(self):
        """Reset framework after each test."""
        reset_framework()

    def test_get_framework_returns_framework_instance(self):
        """Test that get_framework returns a Framework instance."""
        with patch("markwritter.api.services.framework_bridge.SkillRegistry") as mock_registry:
            mock_registry.return_value = MagicMock()
            framework = get_framework()
            assert framework is not None

    def test_get_framework_returns_singleton(self):
        """Test that get_framework returns the same instance."""
        with patch("markwritter.api.services.framework_bridge.SkillRegistry") as mock_registry:
            mock_registry.return_value = MagicMock()
            framework1 = get_framework()
            framework2 = get_framework()
            assert framework1 is framework2

    def test_reset_framework_clears_instance(self):
        """Test that reset_framework clears the cached instance."""
        with patch("markwritter.api.services.framework_bridge.SkillRegistry") as mock_registry:
            mock_registry.return_value = MagicMock()
            framework1 = get_framework()
            reset_framework()
            framework2 = get_framework()
            # Different instances after reset
            assert framework1 is not framework2
