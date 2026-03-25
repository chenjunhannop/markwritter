"""Tests for logging system."""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from markwritter.models import LoggingConfig, OutputConfig, RotationConfig


class TestRotationConfig:
    """Test rotation configuration model."""

    def test_size_rotation_valid(self) -> None:
        """Test valid size rotation config."""
        config = RotationConfig(max_size_mb=10, backup_count=5)
        assert config.max_size_mb == 10
        assert config.backup_count == 5
        assert config.when is None

    def test_time_rotation_valid(self) -> None:
        """Test valid time rotation config."""
        config = RotationConfig(when="D", backup_count=7)
        assert config.when == "D"
        assert config.max_size_mb is None

    def test_missing_both_raises_error(self) -> None:
        """Test that missing both max_size_mb and when raises error."""
        with pytest.raises(ValidationError, match="必须指定 max_size_mb 或 when"):
            RotationConfig()

    def test_both_specified_raises_error(self) -> None:
        """Test that specifying both max_size_mb and when raises error."""
        with pytest.raises(ValidationError, match="不能同时指定"):
            RotationConfig(max_size_mb=10, when="D")

    def test_compress_defaults_to_false(self) -> None:
        """Test that compress defaults to False."""
        config = RotationConfig(max_size_mb=10)
        assert config.compress is False


class TestOutputConfig:
    """Test output configuration model."""

    def test_console_output_valid(self) -> None:
        """Test valid console output config."""
        config = OutputConfig(type="console", format="colored")
        assert config.type == "console"
        assert config.format == "colored"
        assert config.level is None

    def test_file_output_valid(self) -> None:
        """Test valid file output config."""
        from pathlib import Path

        config = OutputConfig(
            type="file",
            path=Path("logs/app.log"),
            format="json",
            rotation=RotationConfig(max_size_mb=10),
        )
        assert config.type == "file"
        assert config.path == Path("logs/app.log")

    def test_file_output_without_path_raises_error(self) -> None:
        """Test that file output without path raises error."""
        with pytest.raises(ValidationError, match="文件输出必须指定 path"):
            OutputConfig(type="file", format="json")

    def test_format_defaults_to_plain(self) -> None:
        """Test that format defaults to plain."""
        config = OutputConfig(type="console")
        assert config.format == "plain"


class TestLoggingConfig:
    """Test logging configuration model."""

    def test_default_config(self) -> None:
        """Test default logging config."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert len(config.outputs) == 1
        assert config.outputs[0].type == "console"

    def test_invalid_level_raises_error(self) -> None:
        """Test that invalid level raises error."""
        with pytest.raises(ValidationError, match="无效的日志级别"):
            LoggingConfig(level="INVALID")

    def test_level_normalized_to_uppercase(self) -> None:
        """Test that level is normalized to uppercase."""
        config = LoggingConfig(level="info")
        assert config.level == "INFO"

    def test_minimal_factory(self) -> None:
        """Test minimal() factory method."""
        config = LoggingConfig.minimal()
        assert config.level == "INFO"
        assert len(config.outputs) == 1
        assert config.outputs[0].format == "colored"

    def test_production_factory(self) -> None:
        """Test production() factory method."""
        from pathlib import Path

        config = LoggingConfig.production(Path("logs"))
        assert len(config.outputs) == 2
        assert config.outputs[0].type == "console"
        assert config.outputs[1].type == "file"
        assert config.outputs[1].rotation is not None


class TestColoredFormatter:
    """Test colored formatter."""

    def test_adds_color_codes(self) -> None:
        """Test that formatter adds ANSI color codes."""
        from markwritter.logger import ColoredFormatter

        formatter = ColoredFormatter(fmt="{levelname} {message}", style="{")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)

        assert "\033[32m" in result  # Green for INFO
        assert "test message" in result
        assert "\033[0m" in result  # Reset code

    def test_debug_uses_cyan(self) -> None:
        """Test that DEBUG level uses cyan color."""
        from markwritter.logger import ColoredFormatter

        formatter = ColoredFormatter(fmt="{levelname}", style="{")
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert "\033[36m" in result  # Cyan

    def test_error_uses_red(self) -> None:
        """Test that ERROR level uses red color."""
        from markwritter.logger import ColoredFormatter

        formatter = ColoredFormatter(fmt="{levelname}", style="{")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert "\033[31m" in result  # Red


class TestJsonFormatter:
    """Test JSON formatter."""

    def test_outputs_valid_json(self) -> None:
        """Test that formatter outputs valid JSON."""
        from markwritter.logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)

        data = json.loads(result)
        assert data["level"] == "INFO"
        assert data["logger"] == "test.module"
        assert data["message"] == "test message"
        assert "timestamp" in data

    def test_includes_extra_fields(self) -> None:
        """Test that extra fields are included in JSON output."""
        from markwritter.logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="skill loaded",
            args=(),
            exc_info=None,
        )
        record.skill_name = "hello"
        record.version = "1.0"

        result = formatter.format(record)
        data = json.loads(result)

        assert data["skill_name"] == "hello"
        assert data["version"] == "1.0"

    def test_timestamp_format(self) -> None:
        """Test that timestamp is in ISO 8601 format."""
        from markwritter.logger import JsonFormatter

        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        data = json.loads(result)

        # Should be parseable as ISO format
        timestamp = data["timestamp"]
        parsed = datetime.fromisoformat(timestamp.rstrip("Z"))
        assert parsed is not None


class TestSetupLogging:
    """Test logging setup."""

    def setup_method(self) -> None:
        """Reset logging before each test."""
        from markwritter.logger import reset_logging

        reset_logging()

    def teardown_method(self) -> None:
        """Reset logging after each test."""
        from markwritter.logger import reset_logging

        reset_logging()

    def test_minimal_config_console_output(self, capsys: pytest.CaptureFixture) -> None:
        """Test minimal config outputs to console."""
        from markwritter.logger import get_logger, setup_logging

        config = LoggingConfig.minimal()
        setup_logging(config=config.model_dump())

        logger = get_logger("test")
        logger.info("test message")

        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_level_filtering(self, capsys: pytest.CaptureFixture) -> None:
        """Test that messages below threshold are filtered."""
        from markwritter.logger import get_logger, setup_logging

        config = LoggingConfig(
            level="WARNING", outputs=[OutputConfig(type="console", format="plain")]
        )
        setup_logging(config=config.model_dump())

        logger = get_logger("test")
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")

        captured = capsys.readouterr()
        assert "debug message" not in captured.out
        assert "info message" not in captured.out
        assert "warning message" in captured.out

    def test_file_output_creates_file(self) -> None:
        """Test that file output creates log file."""
        from markwritter.logger import get_logger, setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            config = LoggingConfig(
                outputs=[OutputConfig(type="file", path=log_path, format="json")]
            )
            setup_logging(config=config.model_dump())

            logger = get_logger("test")
            logger.info("file message")

            assert log_path.exists()
            content = log_path.read_text()
            data = json.loads(content.strip())
            assert data["message"] == "file message"

    def test_multiple_outputs(self, capsys: pytest.CaptureFixture) -> None:
        """Test that multiple outputs work together."""
        from markwritter.logger import get_logger, setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            config = LoggingConfig(
                outputs=[
                    OutputConfig(type="console", format="plain"),
                    OutputConfig(type="file", path=log_path, format="json"),
                ]
            )
            setup_logging(config=config.model_dump())

            logger = get_logger("test")
            logger.info("multi output")

            # Check console
            captured = capsys.readouterr()
            assert "multi output" in captured.out

            # Check file
            content = log_path.read_text()
            data = json.loads(content.strip())
            assert data["message"] == "multi output"

    def test_extra_fields_in_json(self) -> None:
        """Test that extra fields appear in JSON output."""
        from markwritter.logger import get_logger, setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            config = LoggingConfig(
                outputs=[OutputConfig(type="file", path=log_path, format="json")]
            )
            setup_logging(config=config.model_dump())

            logger = get_logger("test")
            logger.info("skill loaded", extra={"skill_name": "hello"})

            content = log_path.read_text()
            data = json.loads(content.strip())
            assert data["skill_name"] == "hello"

    def test_get_logger_returns_markwritter_root(self) -> None:
        """Test that get_logger() without name returns root logger."""
        from markwritter.logger import get_logger, setup_logging

        setup_logging()
        logger = get_logger()
        assert logger.name == "markwritter"

    def test_get_logger_with_name(self) -> None:
        """Test that get_logger(name) returns named logger."""
        from markwritter.logger import get_logger, setup_logging

        setup_logging()
        logger = get_logger("test.module")
        assert logger.name == "markwritter.test.module"

    def test_prevents_double_initialization(self, capsys: pytest.CaptureFixture) -> None:
        """Test that calling setup_logging twice doesn't add duplicate handlers."""
        from markwritter.logger import get_logger, setup_logging

        config = LoggingConfig.minimal()
        setup_logging(config=config.model_dump())
        setup_logging(config=config.model_dump())  # Second call

        logger = get_logger("test")
        logger.info("message")

        captured = capsys.readouterr()
        # Should only appear once (not duplicated)
        assert captured.out.count("message") == 1

    def test_force_reload_clears_handlers(self, capsys: pytest.CaptureFixture) -> None:
        """Test that force_reload clears existing handlers."""
        from markwritter.logger import get_logger, setup_logging

        config = LoggingConfig.minimal()
        setup_logging(config=config.model_dump())
        setup_logging(config=config.model_dump(), force_reload=True)

        logger = get_logger("test")
        logger.info("message")

        captured = capsys.readouterr()
        # Should only appear once
        assert captured.out.count("message") == 1

    def test_config_path_parameter(self, capsys: pytest.CaptureFixture) -> None:
        """Test that config_path parameter loads config from specified path."""
        from markwritter.logger import get_logger, setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "custom_config.yaml"
            config_path.write_text("""
logging:
  level: DEBUG
  outputs:
    - type: console
      format: plain
""")

            setup_logging(config_path=config_path, force_reload=True)

            logger = get_logger("test")
            logger.debug("debug message from custom config")

            captured = capsys.readouterr()
            assert "debug message from custom config" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
