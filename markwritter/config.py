"""Configuration loader for Markwritter framework."""

import os
from pathlib import Path
from typing import Optional

import yaml

from markwritter.models import GlobalConfig


class ConfigError(Exception):
    """Configuration error exception."""

    pass


_config: Optional[GlobalConfig] = None
_config_path: Optional[Path] = None


def load_config(config_path: Optional[Path] = None) -> GlobalConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the config file. If None, will look for
            config.yaml in current directory or use MARKWRITTER_CONFIG_PATH env var.

    Returns:
        GlobalConfig instance

    Raises:
        ConfigError: If config file cannot be loaded or parsed
    """
    global _config, _config_path

    if config_path is None:
        # Check environment variable first
        env_path = os.environ.get("MARKWRITTER_CONFIG_PATH")
        if env_path:
            config_path = Path(env_path)
        else:
            # Look for config.yaml in current directory
            config_path = Path("./config.yaml").resolve()

    _config_path = config_path

    if not config_path.exists():
        # Return default config if file doesn't exist
        _config = GlobalConfig()
        return _config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            data = {}

        _config = GlobalConfig(**data)
        return _config

    except yaml.YAMLError as e:
        raise ConfigError(f"Failed to parse YAML config: {e}") from e
    except Exception as e:
        raise ConfigError(f"Failed to load config: {e}") from e


def get_config() -> GlobalConfig:
    """Get the global configuration singleton.

    Returns:
        GlobalConfig instance. Loads default config if not already loaded.
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> GlobalConfig:
    """Reload configuration from file.

    Returns:
        Reloaded GlobalConfig instance
    """
    global _config, _config_path
    _config = None
    return load_config(_config_path)
