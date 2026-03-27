"""Settings API routes.

Provides endpoints for managing application settings.

Endpoints:
- GET /settings - Get current settings
- PUT /settings - Update settings (partial merge)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

router = APIRouter()

# Module-level state
_data_dir: Optional[str] = None
_settings_cache: dict = {
    "theme": "system",
    "language": "en",
    "vault_path": "",
}

# Fields that are allowed in the public response
_PUBLIC_FIELDS = {"theme", "language", "vault_path"}

# Allowed theme values
_VALID_THEMES = ("light", "dark", "system")

# Default settings
_DEFAULTS = {
    "theme": "system",
    "language": "en",
    "vault_path": "",
}


def init_settings(data_dir: str) -> None:
    """Initialize settings with a data directory for persistence.

    Creates the .markwritter subdirectory if needed and loads existing
    settings from the JSON file.

    Args:
        data_dir: Parent directory for settings storage.
                  Settings file will be at {data_dir}/.markwritter/settings.json.
    """
    global _data_dir, _settings_cache

    _data_dir = data_dir
    settings_dir = Path(data_dir) / ".markwritter"
    try:
        settings_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.warning("Cannot create settings directory %s: %s", settings_dir, exc)
        _settings_cache = dict(_DEFAULTS)
        return

    settings_file = settings_dir / "settings.json"
    if settings_file.exists():
        try:
            raw = settings_file.read_text(encoding="utf-8")
            loaded = json.loads(raw)
            # Merge loaded data with defaults to ensure all keys exist
            merged = {**_DEFAULTS, **loaded}
            _settings_cache = merged
            logger.info("Settings loaded from %s", settings_file)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load settings from %s: %s", settings_file, exc)
            _settings_cache = dict(_DEFAULTS)
    else:
        _settings_cache = dict(_DEFAULTS)


def _save_settings() -> None:
    """Persist current settings cache to the JSON file.

    Does nothing if no data_dir has been configured.
    """
    if _data_dir is None:
        return

    try:
        settings_dir = Path(_data_dir) / ".markwritter"
        settings_dir.mkdir(parents=True, exist_ok=True)
        settings_file = settings_dir / "settings.json"
        settings_file.write_text(
            json.dumps(_settings_cache, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.error("Failed to save settings: %s", exc)


def _get_public_settings() -> dict:
    """Return only the public-safe subset of settings.

    Returns:
        Dict with only the whitelisted public fields.
    """
    return {k: _settings_cache.get(k, _DEFAULTS[k]) for k in _PUBLIC_FIELDS}


# ==============================================================================
# Response / Request Models
# ==============================================================================


class SettingsResponse(BaseModel):
    """Response model for settings."""

    theme: str = "system"
    language: str = "en"
    vault_path: str = ""


class SettingsUpdateRequest(BaseModel):
    """Request model for partial settings update.

    All fields are optional. Only provided fields will be updated.
    """

    theme: Optional[str] = None
    language: Optional[str] = None
    vault_path: Optional[str] = None

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme is one of the allowed values."""
        if v is not None and v not in _VALID_THEMES:
            raise ValueError(f"Invalid theme: '{v}'. Must be one of {list(_VALID_THEMES)}")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language is non-empty."""
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Language cannot be empty")
            return stripped
        return v

    @field_validator("vault_path")
    @classmethod
    def validate_vault_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate vault_path has no path traversal or absolute paths."""
        if v is not None:
            if ".." in v:
                raise ValueError("Vault path must be relative (no '..' allowed)")
            if v.startswith("/"):
                raise ValueError("Vault path must be relative (no leading '/')")
        return v


# ==============================================================================
# Endpoints
# ==============================================================================


@router.get(
    "/",
    response_model=SettingsResponse,
    summary="Get settings",
    description="Get current application settings",
)
async def get_settings() -> SettingsResponse:
    """Get current application settings.

    Returns:
        Current settings as a SettingsResponse.
    """
    public = _get_public_settings()
    return SettingsResponse(**public)


@router.put(
    "/",
    response_model=SettingsResponse,
    summary="Update settings",
    description="Update application settings (partial merge)",
)
async def update_settings(request: SettingsUpdateRequest) -> SettingsResponse:
    """Update application settings.

    Only fields present in the request body are updated. Fields not
    provided retain their current values.

    Args:
        request: Partial update request.

    Returns:
        Updated settings as a SettingsResponse.
    """
    update_data = request.model_dump(exclude_none=True)

    if update_data:
        _settings_cache.update(update_data)
        _save_settings()

    public = _get_public_settings()
    return SettingsResponse(**public)
