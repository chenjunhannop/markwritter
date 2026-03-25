"""Markwritter - A lightweight Agent orchestration framework."""

__version__ = "0.1.0"

from markwritter.core import Framework
from markwritter.executor import SkillExecutor
from markwritter.llm_client import LLMClient, LLMError, MemoryCache
from markwritter.logger import get_logger, reset_logging, setup_logging
from markwritter.models import (
    CacheConfig,
    ExecutionResult,
    GlobalConfig,
    LLMConfig,
    LoggingConfig,
    ModelCapability,
    ModelDefinition,
    OutputConfig,
    ParserConfig,
    ProviderConfig,
    RotationConfig,
    SkillDefinition,
    SkillExecution,
    SkillInput,
    SkillOutput,
)
from markwritter.obsidian import Note, NoteMeta, ObsidianVault
from markwritter.parser import InputParser, ParsedIntent
from markwritter.provider_registry import ProviderRegistry
from markwritter.registry import SkillRegistry

__all__ = [
    "Framework",
    "LLMClient",
    "LLMError",
    "MemoryCache",
    "SkillRegistry",
    "SkillExecutor",
    "InputParser",
    "ParsedIntent",
    "SkillDefinition",
    "SkillExecution",
    "SkillInput",
    "SkillOutput",
    "ExecutionResult",
    "GlobalConfig",
    "LLMConfig",
    "CacheConfig",
    "ParserConfig",
    "LoggingConfig",
    "OutputConfig",
    "RotationConfig",
    "setup_logging",
    "get_logger",
    "reset_logging",
    # Obsidian module
    "Note",
    "NoteMeta",
    "ObsidianVault",
    # Provider Configuration (Phase 1 & 2)
    "ModelCapability",
    "ModelDefinition",
    "ProviderConfig",
    "ProviderRegistry",
]
