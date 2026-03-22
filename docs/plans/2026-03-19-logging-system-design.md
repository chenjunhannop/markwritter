# 日志系统设计

## 概述

为 Markwritter 框架添加生产级日志系统，支持灵活配置、多种输出目标、结构化日志格式。

## 设计目标

1. **生产就绪** - 支持日志轮转、结构化输出、错误降级
2. **零额外依赖** - 使用 Python 标准库 logging
3. **配置驱动** - 通过 config.yaml 灵活配置
4. **开发友好** - 控制台彩色输出，快速定位问题

## 配置结构

```yaml
logging:
  level: INFO  # 全局默认级别

  outputs:
    # 控制台输出 - 开发友好
    - type: console
      level: INFO
      format: colored  # colored / plain / json

    # 文件输出 - 生产就绪
    - type: file
      path: logs/markwritter.log
      level: DEBUG
      format: json
      rotation:
        max_size_mb: 10       # 按大小轮转
        backup_count: 5
        compress: true

    # 可选：错误日志单独存储
    - type: file
      path: logs/error.log
      level: ERROR
      format: json
      rotation:
        when: D               # 按天轮转
        backup_count: 7
```

配置特点：
- **分层级别控制**：全局默认 + 每个 output 可覆盖
- **灵活的输出组合**：可同时配置多个输出目标
- **轮转策略**：`max_size_mb`（按大小）或 `when`（按时间），二选一
- **格式可切换**：colored（控制台）、json（文件）、plain（兼容）

## 模块接口

创建 `markwritter/logger.py`：

```python
def setup_logging(
    config: dict | None = None,
    config_path: Path | None = None,
    force_reload: bool = False,
) -> None:
    """
    根据配置初始化日志系统。

    Args:
        config: 日志配置字典，为 None 时从 config.yaml 加载
        config_path: 配置文件路径
        force_reload: 是否强制重新加载（清除现有 handlers）
    """
    pass


def get_logger(name: str | None = None) -> logging.Logger:
    """
    获取 Logger 实例。

    Args:
        name: logger 名称，通常传 __name__
              为 None 时返回根 logger

    Returns:
        配置好的 Logger 实例
    """
    pass


def reset_logging() -> None:
    """重置日志系统（主要用于测试）。"""
    pass
```

使用示例：

```python
# 在 cli.py 或 core.py 入口
from markwritter.logger import setup_logging
setup_logging()

# 在各模块中
from markwritter.logger import get_logger
logger = get_logger(__name__)

logger.info("Skill loaded", extra={"skill_name": "hello"})
logger.debug("Executing skill", extra={"params": {"name": "World"}})
```

## 核心实现

### 初始化流程

```
setup_logging()
    │
    ▼
检查 _initialized ────(True)───► return
    │ (False)
    ▼
清除现有 handlers
    │
    ▼
加载配置 (config > config_path > 默认)
    │
    ▼
创建根 Logger，设置级别，propagate=False
    │
    ▼
遍历 outputs ──┬──► console → StreamHandler
              ├──► file → RotatingFileHandler / TimedRotatingFileHandler
              │
              ▼
          为每个 Handler 设置 Formatter
              │
              ▼
          注册 Handler 到根 Logger
              │
              ▼
          _initialized = True
              │
              ▼
          (异常) ──► logging.basicConfig 降级
```

### Formatter 实现

#### ColoredFormatter

彩色文本输出，适合控制台：

```python
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
```

输出示例：
```
10:30:00 INFO     [markwritter.core] Skill loaded
10:30:01 WARNING  [markwritter.executor] Timeout exceeded
10:30:02 ERROR    [markwritter.parser] Failed to parse intent
```

#### JsonFormatter

JSON 结构化输出，适合文件和日志平台：

```python
class JsonFormatter(logging.Formatter):
    """JSON 结构化 Formatter，适合文件/日志平台。"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # 添加 extra 字段、异常堆栈等
        return json.dumps(log_data, ensure_ascii=False, default=str)
```

输出示例：
```json
{"timestamp": "2024-01-15T02:30:00.123Z", "level": "INFO", "logger": "markwritter.core", "message": "Skill loaded", "skill_name": "hello"}
{"timestamp": "2024-01-15T02:30:01.456Z", "level": "ERROR", "logger": "markwritter.executor", "message": "Execution failed", "exception": "Traceback..."}
```

### Handler 工厂

```python
def _create_file_handler(output: OutputConfig) -> logging.Handler:
    """创建文件 Handler，支持轮转。"""
    path = output.path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    if output.rotation:
        rotation = output.rotation

        # 按大小轮转
        if rotation.max_size_mb:
            handler = RotatingFileHandler(
                path,
                maxBytes=rotation.max_size_mb * 1024 * 1024,
                backupCount=rotation.backup_count,
            )

        # 按时间轮转
        elif rotation.when:
            handler = TimedRotatingFileHandler(
                path,
                when=rotation.when,
                interval=rotation.interval,
                backupCount=rotation.backup_count,
            )

        # 压缩旧日志
        if rotation.compress:
            # 使用 rotator 和 namer 实现压缩
            pass

    else:
        handler = logging.FileHandler(path)

    return handler
```

### 错误降级处理

```python
def setup_logging(...) -> None:
    try:
        # 正常初始化流程
        _initialized = True
    except Exception as e:
        # 降级处理：基本控制台输出
        logging.basicConfig(
            level=logging.WARNING,
            format="%(levelname)s: %(message)s"
        )
        logging.warning(f"日志初始化失败：{e}，使用降级配置")
        _initialized = True
```

## 模型定义

在 `models.py` 中添加：

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path
from typing import Literal, Optional, Self


class RotationConfig(BaseModel):
    """日志轮转配置。"""

    max_size_mb: Optional[int] = None      # 按大小轮转
    when: Optional[Literal["S", "M", "H", "D", "midnight"]] = None  # 按时间轮转
    interval: int = 1
    backup_count: int = 5
    compress: bool = False                 # 压缩旧日志文件

    @model_validator(mode="after")
    def validate_rotation(self) -> Self:
        if self.max_size_mb is None and self.when is None:
            raise ValueError("必须指定 max_size_mb 或 when")
        if self.max_size_mb is not None and self.when is not None:
            raise ValueError("max_size_mb 和 when 不能同时指定")
        return self


class OutputConfig(BaseModel):
    """日志输出配置。"""

    type: Literal["console", "file"]
    level: Optional[str] = None
    format: Literal["colored", "json", "plain"] = "plain"
    template: Optional[str] = None

    # 文件输出专用
    path: Optional[Path] = None
    rotation: Optional[RotationConfig] = None

    @model_validator(mode="after")
    def validate_file_output(self) -> Self:
        if self.type == "file" and self.path is None:
            raise ValueError("文件输出必须指定 path")
        return self


class LoggingConfig(BaseModel):
    """日志系统配置。"""

    level: str = "INFO"
    outputs: list[OutputConfig] = Field(default_factory=lambda: [
        OutputConfig(type="console", format="colored", level="INFO"),
    ])

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid_levels:
            raise ValueError(f"无效的日志级别: {v}, 有效值: {valid_levels}")
        return upper

    @classmethod
    def minimal(cls) -> Self:
        """创建最小配置（仅控制台）。"""
        return cls(
            level="INFO",
            outputs=[OutputConfig(type="console", format="colored")]
        )

    @classmethod
    def production(cls, log_dir: Path = Path("logs")) -> Self:
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

## 集成点

### CLI 入口 (cli.py)

```python
from markwritter.logger import setup_logging
from markwritter.config import get_config

def main():
    setup_logging()  # 自动读取 config.yaml
    # ... 其他初始化
```

### 配置加载 (config.py)

```python
from markwritter.models import LoggingConfig

class GlobalConfig(BaseModel):
    logging: LoggingConfig = Field(default_factory=LoggingConfig.minimal)
```

## 测试策略

### 单元测试

```python
class TestLoggingConfig:
    """测试日志配置模型。"""

    def test_rotation_config_size(self):
        """测试按大小轮转配置。"""
        config = RotationConfig(max_size_mb=10, backup_count=5)
        assert config.max_size_mb == 10
        assert config.backup_count == 5

    def test_rotation_config_time(self):
        """测试按时间轮转配置。"""
        config = RotationConfig(when="D", backup_count=7)
        assert config.when == "D"

    def test_rotation_config_invalid(self):
        """测试无效轮转配置。"""
        with pytest.raises(ValidationError):
            RotationConfig()  # 必须指定 max_size_mb 或 when

        with pytest.raises(ValidationError):
            RotationConfig(max_size_mb=10, when="D")  # 不能同时指定


class TestFormatters:
    """测试 Formatter 输出。"""

    def test_colored_formatter(self):
        """测试彩色格式输出。"""
        formatter = ColoredFormatter(fmt="{levelname} {message}", style="{")
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        result = formatter.format(record)
        assert "\033[32m" in result  # Green color
        assert "test message" in result

    def test_json_formatter(self):
        """测试 JSON 格式输出。"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        result = formatter.format(record)
        data = json.loads(result)
        assert data["level"] == "INFO"
        assert data["message"] == "test message"
        assert "timestamp" in data
```

### 集成测试

```python
class TestLoggingSetup:
    """测试日志初始化。"""

    def setup_method(self):
        reset_logging()

    def teardown_method(self):
        reset_logging()

    def test_minimal_config(self, capsys):
        """测试最小配置。"""
        config = LoggingConfig.minimal()
        setup_logging(config=config.model_dump())

        logger = get_logger("test")
        logger.info("test message")

        captured = capsys.readouterr()
        assert "test message" in captured.out

    def test_multiple_outputs(self, tmp_path, capsys):
        """测试多输出组合。"""
        log_file = tmp_path / "test.log"
        config = LoggingConfig(
            outputs=[
                OutputConfig(type="console", format="plain"),
                OutputConfig(type="file", path=log_file, format="json"),
            ]
        )
        setup_logging(config=config.model_dump())

        logger = get_logger("test")
        logger.info("test message")

        # 检查控制台输出
        captured = capsys.readouterr()
        assert "test message" in captured.out

        # 检查文件输出
        assert log_file.exists()
        content = log_file.read_text()
        data = json.loads(content.strip())
        assert data["message"] == "test message"

    def test_level_filtering(self, capsys):
        """测试级别过滤。"""
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

    def test_extra_fields(self, tmp_path):
        """测试 extra 字段传递到 JSON。"""
        log_file = tmp_path / "test.log"
        config = LoggingConfig(
            outputs=[OutputConfig(type="file", path=log_file, format="json")]
        )
        setup_logging(config=config.model_dump())

        logger = get_logger("test")
        logger.info("skill loaded", extra={"skill_name": "hello", "version": "1.0"})

        content = log_file.read_text()
        data = json.loads(content.strip())
        assert data["skill_name"] == "hello"
        assert data["version"] == "1.0"
```

### 快照测试

```python
class TestJsonSnapshot:
    """测试 JSON 输出结构。"""

    def test_json_structure(self, tmp_path, snapshot):
        """验证 JSON 输出结构。"""
        log_file = tmp_path / "test.log"
        config = LoggingConfig(
            outputs=[OutputConfig(type="file", path=log_file, format="json")]
        )
        setup_logging(config=config.model_dump())

        logger = get_logger("test.module")
        logger.info("test message", extra={"key": "value"})

        content = log_file.read_text()
        data = json.loads(content.strip())

        # 验证必需字段
        assert set(data.keys()) >= {"timestamp", "level", "logger", "message", "key"}
        assert data["level"] == "INFO"
        assert data["logger"] == "test.module"
        assert data["message"] == "test message"
        assert data["key"] == "value"

        # 验证时间戳格式
        datetime.fromisoformat(data["timestamp"].rstrip("Z"))
```

### 覆盖率目标

- 核心代码（logger.py、models.py 中的日志相关部分）：**100%**
- 边缘场景：错误降级、无效配置、文件创建失败

## 文件清单

```
markwritter/
├── logger.py              # 新增：日志系统核心实现
├── models.py              # 修改：添加 LoggingConfig 等模型
├── config.py              # 修改：集成日志配置
├── cli.py                 # 修改：启动时调用 setup_logging()
config.yaml                # 修改：添加 logging 配置段
tests/
└── test_logger.py         # 新增：日志系统测试
```

## 实现顺序

1. 添加模型定义（models.py）
2. 实现 logger.py 核心逻辑
3. 更新 config.py 集成
4. 更新 cli.py 调用
5. 编写测试
6. 更新 config.yaml 示例

---

设计日期：2026-03-19