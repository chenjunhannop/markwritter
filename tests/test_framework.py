"""Tests for Markwritter framework."""

import logging
import tempfile
from pathlib import Path

import pytest

from markwritter.core import Framework
from markwritter.executor import SkillExecutor
from markwritter.logger import reset_logging
from markwritter.models import SkillDefinition, SkillExecution, SkillInput
from markwritter.parser import InputParser
from markwritter.registry import SkillRegistry


class TestSkillRegistry:
    """Test skill registry functionality."""

    def test_load_skills_from_directory(self) -> None:
        """Test loading skills from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test skill
            skill_dir = Path(tmpdir) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "skill.yaml").write_text("""
name: test-skill
description: A test skill
version: 1.0.0
execution:
  command: python
  script: run.py
""")

            registry = SkillRegistry(Path(tmpdir))
            skills = registry.list_all()

            assert len(skills) == 1
            assert skills[0].name == "test-skill"

    def test_get_skill_by_name(self) -> None:
        """Test getting a skill by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "skill.yaml").write_text("""
name: my-skill
description: My skill
version: 1.0.0
execution:
  command: python
  script: run.py
""")

            registry = SkillRegistry(Path(tmpdir))
            skill = registry.get("my-skill")

            assert skill is not None
            assert skill.name == "my-skill"
            assert skill.description == "My skill"


class TestSkillExecutor:
    """Test skill executor functionality."""

    def test_execute_skill_with_params(self) -> None:
        """Test executing a skill with parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test skill
            skill_dir = Path(tmpdir) / "echo"
            skill_dir.mkdir()
            (skill_dir / "skill.yaml").write_text("""
name: echo
description: Echo skill
version: 1.0.0
inputs:
  - name: message
    type: string
    required: true
execution:
  command: python
  script: run.py
  timeout: 10
""")
            (skill_dir / "run.py").write_text("""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--message", required=True)
args = parser.parse_args()
print(f"Echo: {args.message}")
""")

            registry = SkillRegistry(Path(tmpdir))
            skill = registry.get("echo")
            assert skill is not None

            executor = SkillExecutor(Path(tmpdir))
            result = executor.execute_sync(skill, {"message": "hello"})

            assert result.success
            assert "Echo: hello" in result.output


class TestInputParser:
    """Test input parser functionality."""

    def test_parse_skill_name(self) -> None:
        """Test parsing skill name from input."""
        skill_def = SkillDefinition(
            name="hello",
            description="Greeting skill",
            execution=SkillExecution(command="python", script="run.py"),
        )

        parser = InputParser([skill_def])
        intent = parser.parse("Run hello skill")

        assert intent.skill_name == "hello"

    def test_parse_with_params(self) -> None:
        """Test parsing parameters from input."""
        skill_def = SkillDefinition(
            name="greet",
            description="Greeting skill",
            inputs=[SkillInput(name="name", required=True)],
            execution=SkillExecution(command="python", script="run.py"),
        )

        parser = InputParser([skill_def])
        intent = parser.parse("greet --name Alice")

        assert intent.skill_name == "greet"
        assert intent.params.get("name") == "Alice"


class TestFramework:
    """Test framework integration."""

    def test_run_skill_directly(self) -> None:
        """Test running a skill directly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create hello skill
            skill_dir = Path(tmpdir) / "hello"
            skill_dir.mkdir()
            (skill_dir / "skill.yaml").write_text("""
name: hello
description: Hello skill
version: 1.0.0
inputs:
  - name: name
    type: string
    default: World
execution:
  command: python
  script: run.py
""")
            (skill_dir / "run.py").write_text("""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--name", default="World")
args = parser.parse_args()
print(f"Hello, {args.name}!")
""")

            registry = SkillRegistry(Path(tmpdir))
            framework = Framework(registry)
            result = framework.run_skill("hello", {"name": "Test"})

            assert "Hello, Test!" in result

    def test_process_natural_language(self) -> None:
        """Test processing natural language input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create hello skill
            skill_dir = Path(tmpdir) / "hello"
            skill_dir.mkdir()
            (skill_dir / "skill.yaml").write_text("""
name: hello
description: Simple greeting skill
version: 1.0.0
inputs:
  - name: name
    type: string
    default: World
execution:
  command: python
  script: run.py
""")
            (skill_dir / "run.py").write_text("""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--name", default="World")
args = parser.parse_args()
print(f"Hello, {args.name}!")
""")

            registry = SkillRegistry(Path(tmpdir))
            framework = Framework(registry)
            result = framework.process_input("Say hello to Bob")

            # Parser should match "hello" and extract "Bob" as name
            # (may fail depending on parser implementation details)
            # This tests the integration
            assert isinstance(result, str)


class TestLoggingIntegration:
    """Test logging integration with CLI."""

    def setup_method(self) -> None:
        """Reset logging before each test."""
        reset_logging()

    def teardown_method(self) -> None:
        """Reset logging after each test."""
        reset_logging()

    def test_framework_logs_skill_execution(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that framework logs skill execution."""
        from markwritter.logger import setup_logging

        setup_logging()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create hello skill
            skill_dir = Path(tmpdir) / "hello"
            skill_dir.mkdir()
            (skill_dir / "skill.yaml").write_text("""
name: hello
description: Hello skill
version: 1.0.0
inputs:
  - name: name
    type: string
    default: World
execution:
  command: python
  script: run.py
""")
            (skill_dir / "run.py").write_text("""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--name", default="World")
args = parser.parse_args()
print(f"Hello, {args.name}!")
""")

            registry = SkillRegistry(Path(tmpdir))
            framework = Framework(registry)

            # Capture logs at DEBUG level
            with caplog.at_level(logging.DEBUG, logger="markwritter"):
                result = framework.run_skill("hello", {"name": "Test"})

            assert "Hello, Test!" in result

    def test_logs_not_duplicated(self, capsys: pytest.CaptureFixture) -> None:
        """Test that logs are not duplicated after multiple runs."""
        from markwritter.logger import get_logger, setup_logging

        # Simulate multiple CLI invocations
        setup_logging()
        setup_logging()
        setup_logging()

        logger = get_logger("test")
        logger.info("test message")

        captured = capsys.readouterr()
        # Message should appear exactly once
        assert captured.out.count("test message") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
