"""Logging system for Markwritter framework."""

import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from markwritter.models import LoggingConfig, OutputConfig

# Global state
_initialized = False


class ColoredFormatter(logging.Formatter):
    """彩色文本 Formatter，适合控制台输出。"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
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


class JsonFormatter(logging.Formatter):
    """JSON 结构化 Formatter，适合文件/日志平台。"""

    # Standard LogRecord attributes to exclude
    EXCLUDE_FIELDS = {
        "msg",
        "args",
        "levelname",
        "name",
        "message",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "process",
        "processName",
        "filename",
        "module",
        "lineno",
        "funcName",
        "pathname",
        "exc_info",
        "exc_text",
        "stack_info",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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


def _create_formatter(output: OutputConfig) -> logging.Formatter:
    """根据配置创建 Formatter。"""
    if output.format == "json":
        return JsonFormatter()
    elif output.format == "colored":
        return ColoredFormatter(
            fmt=output.template or "{asctime} {levelname:8} [{name}] {message}",
            style="{",
            datefmt="%H:%M:%S",
        )
    else:  # plain
        return logging.Formatter(
            fmt=output.template or "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
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
        if config is not None:
            log_config = LoggingConfig(**config)
        elif config_path is not None:
            from markwritter.config import load_config

            global_config = load_config(config_path)
            log_config = global_config.logging
        else:
            from markwritter.config import get_config

            global_config = get_config()
            log_config = global_config.logging

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
        logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
        logging.warning(f"日志初始化失败：{e}，使用降级配置")
        _initialized = True


def reset_logging() -> None:
    """重置日志系统（主要用于测试）。"""
    global _initialized
    logger = logging.getLogger("markwritter")
    logger.handlers.clear()
    _initialized = False


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取 Logger 实例。

    Args:
        name: Logger 名称，为 None 时返回 markwritter 根 logger。
              如果提供名称，将返回 markwritter.<name> 子 logger。

    Returns:
        logging.Logger: 配置好的 Logger 实例
    """
    if name is None:
        return logging.getLogger("markwritter")
    return logging.getLogger(f"markwritter.{name}")


__all__ = ["setup_logging", "get_logger", "reset_logging"]
