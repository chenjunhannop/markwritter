# 日志系统实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 Markwritter 框架添加生产级日志系统，支持配置驱动的多输出目标和结构化日志格式。

**Architecture:** 使用 Python 标准库 logging，封装 setup_logging/get_logger/reset_logging 接口。支持 console/file 两种输出类型，colored/json/plain 三种格式，按大小/时间两种轮转策略。

**Tech Stack:** Python 3.10+, logging, Pydantic, YAML

---

## Task 1: 添加日志配置模型

**Files:**
- Modify: `markwritter/models.py:88-94`
- Test: `tests/test_logger.py`

### Step 1: 创建测试文件，编写配置模型测试

创建 `tests/test_logger.py`:

```python
"""Tests for logging system."""

import pytest
from pydantic import ValidationError

from markwritter.models import RotationConfig, OutputConfig, LoggingConfig


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
            rotation=RotationConfig(max_size_mb=10)
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
```

### Step 2: 运行测试确认失败

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py -v`

Expected: FAIL - ModuleNotFoundError or ImportError (模型尚未定义)

### Step 3: 添加 RotationConfig 模型

在 `markwritter/models.py` 中，在 `ParserConfig` 类之后添加：

```python
class RotationConfig(BaseModel):
    """日志轮转配置。"""

    max_size_mb: Optional[int] = None
    when: Optional[Literal["S", "M", "H", "D", "midnight"]] = None
    interval: int = 1
    backup_count: int = 5
    compress: bool = False

    @model_validator(mode="after")
    def validate_rotation(self) -> "RotationConfig":
        if self.max_size_mb is None and self.when is None:
            raise ValueError("必须指定 max_size_mb 或 when")
        if self.max_size_mb is not None and self.when is not None:
            raise ValueError("max_size_mb 和 when 不能同时指定")
        return self
```

需要在文件顶部添加导入：
```python
from typing import Any, Literal, Optional, Self
```

### Step 4: 运行测试确认 RotationConfig 通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestRotationConfig -v`

Expected: PASS (部分测试)

### Step 5: 添加 OutputConfig 模型

在 `RotationConfig` 之后添加：

```python
class OutputConfig(BaseModel):
    """日志输出配置。"""

    type: Literal["console", "file"]
    level: Optional[str] = None
    format: Literal["colored", "json", "plain"] = "plain"
    template: Optional[str] = None
    path: Optional[Path] = None
    rotation: Optional[RotationConfig] = None

    @model_validator(mode="after")
    def validate_file_output(self) -> "OutputConfig":
        if self.type == "file" and self.path is None:
            raise ValueError("文件输出必须指定 path")
        return self
```

### Step 6: 运行测试确认 OutputConfig 通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestOutputConfig -v`

Expected: PASS

### Step 7: 添加 LoggingConfig 模型

在 `OutputConfig` 之后添加：

```python
class LoggingConfig(BaseModel):
    """日志系统配置。"""

    level: str = "INFO"
    outputs: list[OutputConfig] = Field(
        default_factory=lambda: [OutputConfig(type="console", format="colored", level="INFO")]
    )

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid_levels:
            raise ValueError(f"无效的日志级别: {v}, 有效值: {valid_levels}")
        return upper

    @classmethod
    def minimal(cls) -> "Self":
        """创建最小配置（仅控制台）。"""
        return cls(
            level="INFO",
            outputs=[OutputConfig(type="console", format="colored")]
        )

    @classmethod
    def production(cls, log_dir: Path = Path("logs")) -> "Self":
        """创建生产配置（控制台 + 文件）。"""
        return cls(
            level="INFO",
            outputs=[
                OutputConfig(type="console", format="colored", level="INFO"),
                OutputConfig(
                    type="file",
                    path=log_dir / "app.log",
                    format="json",
                    level="DEBUG",
                    rotation=RotationConfig(max_size_mb=10, backup_count=5, compress=True)
                ),
            ]
        )
```

需要添加 `field_validator` 和 `model_validator` 导入：
```python
from pydantic import BaseModel, Field, field_validator, model_validator
```

### Step 8: 运行测试确认 LoggingConfig 通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestLoggingConfig -v`

Expected: PASS

### Step 9: 更新 GlobalConfig 添加 logging 字段

修改 `GlobalConfig` 类：

```python
class GlobalConfig(BaseModel):
    """Global configuration root model."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    parser: ParserConfig = Field(default_factory=ParserConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig.minimal)
```

### Step 10: 运行所有测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py -v`

Expected: PASS (所有测试)

### Step 11: 提交

```bash
git add markwritter/models.py tests/test_logger.py
git commit -m "feat: add logging configuration models"
```

---

## Task 2: 实现 ColoredFormatter 和 JsonFormatter

**Files:**
- Create: `markwritter/logger.py`
- Test: `tests/test_logger.py`

### Step 1: 添加 Formatter 测试

在 `tests/test_logger.py` 末尾添加：

```python
import json
import logging


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
        from datetime import datetime

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
```

### Step 2: 运行测试确认失败

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestColoredFormatter tests/test_logger.py::TestJsonFormatter -v`

Expected: FAIL - ModuleNotFoundError

### Step 3: 创建 logger.py 并实现 ColoredFormatter

创建 `markwritter/logger.py`:

```python
"""Logging system for Markwritter framework."""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from markwritter.models import LoggingConfig, OutputConfig


# Global state
_initialized = False


class ColoredFormatter(logging.Formatter):
    """彩色文本 Formatter，适合控制台输出。"""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Save original level name
        original_levelname = record.levelname

        # Add color
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        # Format
        result = super().format(record)

        # Restore original level name
        record.levelname = original_levelname

        return result
```

### Step 4: 运行 ColoredFormatter 测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestColoredFormatter -v`

Expected: PASS

### Step 5: 实现 JsonFormatter

在 `logger.py` 的 `ColoredFormatter` 之后添加：

```python
class JsonFormatter(logging.Formatter):
    """JSON 结构化 Formatter，适合文件/日志平台。"""

    # Standard LogRecord attributes to exclude
    EXCLUDE_FIELDS = {
        "msg", "args", "levelname", "name", "message",
        "created", "msecs", "relativeCreated",
        "thread", "threadName", "process", "processName",
        "filename", "module", "lineno", "funcName",
        "pathname", "exc_info", "exc_text", "stack_info",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in self.EXCLUDE_FIELDS:
                log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False, default=str)
```

### Step 6: 运行 JsonFormatter 测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestJsonFormatter -v`

Expected: PASS

### Step 7: 运行所有 Formatter 测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py -v`

Expected: PASS (所有测试)

### Step 8: 提交

```bash
git add markwritter/logger.py tests/test_logger.py
git commit -m "feat: implement ColoredFormatter and JsonFormatter"
```

---

## Task 3: 实现 Handler 工厂和 setup_logging

**Files:**
- Modify: `markwritter/logger.py`
- Test: `tests/test_logger.py`

### Step 1: 添加集成测试

在 `tests/test_logger.py` 末尾添加：

```python
import tempfile
from pathlib import Path


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
        from markwritter.logger import setup_logging, get_logger

        config = LoggingConfig.minimal()
        setup_logging(config=config.model_dump())

        logger = get_logger("test")
        logger.info("test message")

        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_level_filtering(self, capsys: pytest.CaptureFixture) -> None:
        """Test that messages below threshold are filtered."""
        from markwritter.logger import setup_logging, get_logger

        config = LoggingConfig(
            level="WARNING",
            outputs=[OutputConfig(type="console", format="plain")]
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
        from markwritter.logger import setup_logging, get_logger

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            config = LoggingConfig(
                outputs=[
                    OutputConfig(type="file", path=log_path, format="json")
                ]
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
        from markwritter.logger import setup_logging, get_logger

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
        from markwritter.logger import setup_logging, get_logger

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            config = LoggingConfig(
                outputs=[
                    OutputConfig(type="file", path=log_path, format="json")
                ]
            )
            setup_logging(config=config.model_dump())

            logger = get_logger("test")
            logger.info("skill loaded", extra={"skill_name": "hello"})

            content = log_path.read_text()
            data = json.loads(content.strip())
            assert data["skill_name"] == "hello"

    def test_get_logger_returns_markwritter_root(self) -> None:
        """Test that get_logger() without name returns root logger."""
        from markwritter.logger import setup_logging, get_logger

        setup_logging()
        logger = get_logger()
        assert logger.name == "markwritter"

    def test_get_logger_with_name(self) -> None:
        """Test that get_logger(name) returns named logger."""
        from markwritter.logger import setup_logging, get_logger

        setup_logging()
        logger = get_logger("test.module")
        assert logger.name == "test.module"

    def test_prevents_double_initialization(self, capsys: pytest.CaptureFixture) -> None:
        """Test that calling setup_logging twice doesn't add duplicate handlers."""
        from markwritter.logger import setup_logging, get_logger

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
        from markwritter.logger import setup_logging, get_logger

        config = LoggingConfig.minimal()
        setup_logging(config=config.model_dump())
        setup_logging(config=config.model_dump(), force_reload=True)

        logger = get_logger("test")
        logger.info("message")

        captured = capsys.readouterr()
        # Should only appear once
        assert captured.out.count("message") == 1
```

### Step 2: 运行测试确认失败

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestSetupLogging -v`

Expected: FAIL - ImportError (函数未定义)

### Step 3: 实现 Handler 工厂函数

在 `logger.py` 中，`JsonFormatter` 之后添加：

```python
def _create_formatter(output: OutputConfig) -> logging.Formatter:
    """根据配置创建 Formatter。"""
    if output.format == "json":
        return JsonFormatter()
    elif output.format == "colored":
        return ColoredFormatter(
            fmt=output.template or "{asctime} {levelname:8} [{name}] {message}",
            style="{",
            datefmt="%H:%M:%S"
        )
    else:  # plain
        return logging.Formatter(
            fmt=output.template or "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def _create_file_handler(output: OutputConfig) -> logging.Handler:
    """创建文件 Handler，支持轮转。"""
    path = output.path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    if output.rotation:
        rotation = output.rotation

        # 按大小轮转
        if rotation.max_size_mb:
            return RotatingFileHandler(
                path,
                maxBytes=rotation.max_size_mb * 1024 * 1024,
                backupCount=rotation.backup_count,
            )
        # 按时间轮转
        elif rotation.when:
            return TimedRotatingFileHandler(
                path,
                when=rotation.when,
                interval=rotation.interval,
                backupCount=rotation.backup_count,
            )

    return logging.FileHandler(path)


def _create_handler(output: OutputConfig) -> logging.Handler:
    """根据配置创建 Handler。"""
    if output.type == "console":
        handler = logging.StreamHandler(sys.stdout)
    elif output.type == "file":
        handler = _create_file_handler(output)
    else:
        raise ValueError(f"未知的 output 类型：{output.type}")

    # Set level if specified
    if output.level:
        handler.setLevel(output.level.upper())

    return handler
```

### Step 4: 实现 setup_logging 和辅助函数

在 `_create_handler` 之后添加：

```python
def setup_logging(
    config: Optional[dict] = None,
    config_path: Optional[Path] = None,
    force_reload: bool = False,
) -> None:
    """
    根据配置初始化日志系统。

    Args:
        config: 日志配置字典，为 None 时从 config.yaml 加载
        config_path: 配置文件路径
        force_reload: 是否强制重新加载（清除现有 handlers）
    """
    global _initialized

    if _initialized and not force_reload:
        return

    # Get root logger
    root_logger = logging.getLogger("markwritter")
    root_logger.handlers.clear()

    try:
        # Load configuration
        if config is None:
            from markwritter.config import get_config
            global_config = get_config()
            log_config = global_config.logging
        else:
            log_config = LoggingConfig(**config)

        # Set root logger level
        root_logger.setLevel(log_config.level.upper())
        root_logger.propagate = False

        # Create handlers for each output
        for output in log_config.outputs:
            handler = _create_handler(output)
            formatter = _create_formatter(output)
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)

        _initialized = True

    except Exception as e:
        # Fallback to basic config
        logging.basicConfig(
            level=logging.WARNING,
            format="%(levelname)s: %(message)s"
        )
        logging.warning(f"日志初始化失败：{e}，使用降级配置")
        _initialized = True


def reset_logging() -> None:
    """重置日志系统（主要用于测试）。"""
    global _initialized
    logger = logging.getLogger("markwritter")
    logger.handlers.clear()
    _initialized = False


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取 Logger 实例。"""
    if name is None:
        return logging.getLogger("markwritter")
    return logging.getLogger(name)


__all__ = ["setup_logging", "get_logger", "reset_logging"]
```

### Step 5: 运行测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py::TestSetupLogging -v`

Expected: PASS

### Step 6: 运行所有测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_logger.py -v`

Expected: PASS (所有测试)

### Step 7: 提交

```bash
git add markwritter/logger.py tests/test_logger.py
git commit -m "feat: implement setup_logging with Handler factory"
```

---

## Task 4: 更新 CLI 集成日志系统

**Files:**
- Modify: `markwritter/cli.py`
- Test: `tests/test_framework.py`

### Step 1: 添加 CLI 集成测试

在 `tests/test_framework.py` 中添加导入和测试：

```python
import pytest
from pathlib import Path
import tempfile
import shutil
import logging

from markwritter.models import SkillDefinition, SkillInput, SkillOutput, SkillExecution
from markwritter.registry import SkillRegistry
from markwritter.executor import SkillExecutor
from markwritter.parser import InputParser
from markwritter.core import Framework
from markwritter.logger import reset_logging


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
        from markwritter.logger import setup_logging, get_logger

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
        from markwritter.logger import setup_logging, get_logger

        # Simulate multiple CLI invocations
        setup_logging()
        setup_logging()
        setup_logging()

        logger = get_logger("test")
        logger.info("test message")

        captured = capsys.readouterr()
        # Message should appear exactly once
        assert captured.out.count("test message") == 1
```

### Step 2: 运行测试确认失败

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_framework.py::TestLoggingIntegration -v`

Expected: PASS (基础功能已有，但日志未初始化)

### Step 3: 更新 cli.py 集成日志初始化

修改 `markwritter/cli.py`:

在导入部分添加：
```python
from markwritter.logger import setup_logging
```

修改 `get_framework()` 函数：
```python
def get_framework() -> Framework:
    """Get or create framework instance."""
    global _framework
    if _framework is None:
        setup_logging()  # Initialize logging
        skills_dir = Path("./skills").resolve()
        registry = SkillRegistry(skills_dir)
        _framework = Framework(registry)
    return _framework
```

### Step 4: 运行测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/test_framework.py::TestLoggingIntegration -v`

Expected: PASS

### Step 5: 运行所有测试确认无回归

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/ -v`

Expected: PASS (所有测试)

### Step 6: 提交

```bash
git add markwritter/cli.py tests/test_framework.py
git commit -m "feat: integrate logging into CLI entry point"
```

---

## Task 5: 更新 config.yaml 示例

**Files:**
- Modify: `config.yaml`

### Step 1: 更新 config.yaml 添加日志配置

修改 `config.yaml`:

```yaml
llm:
  default_model: "qwen/qwen3.5-plus"
  timeout: 30
  max_retries: 2
  temperature: 0.1

cache:
  enabled: true
  ttl_seconds: 3600
  max_size: 1000

parser:
  confidence_threshold: 0.7

# Logging configuration
logging:
  level: INFO

  outputs:
    # Console output - developer friendly
    - type: console
      level: INFO
      format: colored

    # File output - production ready
    - type: file
      path: logs/markwritter.log
      level: DEBUG
      format: json
      rotation:
        max_size_mb: 10
        backup_count: 5
        compress: true
```

### Step 2: 运行测试确认配置可加载

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/ -v`

Expected: PASS

### Step 3: 提交

```bash
git add config.yaml
git commit -m "docs: add logging configuration to config.yaml"
```

---

## Task 6: 更新 __init__.py 导出

**Files:**
- Modify: `markwritter/__init__.py`

### Step 1: 更新 __init__.py 导出日志接口

修改 `markwritter/__init__.py`，添加日志相关导出：

```python
"""Markwritter - A lightweight Agent orchestration framework."""

from markwritter.core import Framework
from markwritter.models import (
    SkillDefinition,
    SkillInput,
    SkillOutput,
    SkillExecution,
    ExecutionResult,
    GlobalConfig,
    LoggingConfig,
    OutputConfig,
    RotationConfig,
)
from markwritter.logger import setup_logging, get_logger, reset_logging
from markwritter.registry import SkillRegistry
from markwritter.executor import SkillExecutor
from markwritter.parser import InputParser

__version__ = "0.1.0"

__all__ = [
    "Framework",
    "SkillDefinition",
    "SkillInput",
    "SkillOutput",
    "SkillExecution",
    "ExecutionResult",
    "GlobalConfig",
    "LoggingConfig",
    "OutputConfig",
    "RotationConfig",
    "setup_logging",
    "get_logger",
    "reset_logging",
    "SkillRegistry",
    "SkillExecutor",
    "InputParser",
]
```

### Step 2: 运行所有测试确认通过

Run: `cd /Users/chenjunhan/dev/github-project/markwritter && source venv/bin/activate && pytest tests/ -v`

Expected: PASS

### Step 3: 提交

```bash
git add markwritter/__init__.py
git commit -m "feat: export logging interfaces from __init__.py"
```

---

## Final Verification

### Run all tests with coverage

```bash
cd /Users/chenjunhan/dev/github-project/markwritter
source venv/bin/activate
pytest tests/ -v --cov=markwritter --cov-report=term-missing
```

Expected: All tests pass, coverage >= 80%

### Verify linting

```bash
cd /Users/chenjunhan/dev/github-project/markwritter
source venv/bin/activate
ruff check markwritter/
black --check markwritter/
```

Expected: No errors

---

## Summary

| Task | Description | Files Modified |
|------|-------------|----------------|
| 1 | 添加日志配置模型 | models.py, test_logger.py |
| 2 | 实现 Formatter | logger.py, test_logger.py |
| 3 | 实现 setup_logging | logger.py, test_logger.py |
| 4 | CLI 集成 | cli.py, test_framework.py |
| 5 | 更新配置示例 | config.yaml |
| 6 | 导出接口 | __init__.py |

**Estimated total steps:** 32 steps across 6 tasks