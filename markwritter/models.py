"""Pydantic models for Markwritter framework."""

from pathlib import Path
from typing import Any, Literal, Optional, Self

from pydantic import BaseModel, Field, field_validator, model_validator

# =============================================================================
# Phase 1: Provider Configuration Models
# =============================================================================


class ModelCapability(BaseModel):
    """Model capability declarations.

    Describes what capabilities a model supports.
    """

    vision: bool = False
    tools: bool = False
    streaming: bool = False


class ModelDefinition(BaseModel):
    """Model definition for a specific model within a provider.

    Defines the properties and capabilities of a model.
    """

    id: str
    name: Optional[str] = None
    capabilities: ModelCapability = Field(default_factory=ModelCapability)
    context_window: int = 4096
    max_tokens: int = 4096


class ProviderConfig(BaseModel):
    """LLM provider configuration.

    Defines a provider and its associated models.
    """

    name: str
    provider_type: Literal["openai", "anthropic", "google", "openai-compatible"]
    api_key_env: str
    base_url: Optional[str] = None
    models: list[ModelDefinition] = Field(default_factory=list)
    is_default: bool = False


# =============================================================================
# Core Configuration Models
# =============================================================================


class SkillInput(BaseModel):
    """Definition of a skill input parameter."""

    name: str
    type: str = "string"
    description: str = ""
    required: bool = True
    default: Optional[Any] = None


class SkillOutput(BaseModel):
    """Definition of a skill output."""

    type: str = "string"
    description: str = ""


class SkillExecution(BaseModel):
    """Execution configuration for a skill."""

    command: str
    script: str
    working_dir: Optional[str] = None
    timeout: int = 60


class SkillDefinition(BaseModel):
    """Complete skill definition from YAML."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    inputs: list[SkillInput] = Field(default_factory=list)
    output: SkillOutput = Field(default_factory=lambda: SkillOutput())
    execution: SkillExecution

    @classmethod
    def from_yaml(cls, path: Path) -> "SkillDefinition":
        """Load skill definition from YAML file."""
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(**data)


class ExecutionResult(BaseModel):
    """Result of skill execution."""

    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0


class LLMConfig(BaseModel):
    """LLM configuration model.

    Supports multiple providers with model definitions and fallback chains.
    """

    default_model: str = "qwen/qwen3.5-plus"
    timeout: int = 30
    max_retries: int = 2
    temperature: float = 0.1
    providers: list[ProviderConfig] = Field(default_factory=list)
    fallback_chain: list[str] = Field(default_factory=list)


class CacheConfig(BaseModel):
    """Cache configuration model."""

    enabled: bool = True
    ttl_seconds: int = 3600
    max_size: int = 1000


class ParserConfig(BaseModel):
    """Parser configuration model."""

    confidence_threshold: float = 0.7


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
        return cls(level="INFO", outputs=[OutputConfig(type="console", format="colored")])

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
                    rotation=RotationConfig(max_size_mb=10, backup_count=5, compress=True),
                ),
            ],
        )


class GlobalConfig(BaseModel):
    """Global configuration root model."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    parser: ParserConfig = Field(default_factory=ParserConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig.minimal)
