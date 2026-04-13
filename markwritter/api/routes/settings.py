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
from typing import Callable, Optional

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
    "api_url": "",
    "llm_model": "gpt-4",
    "api_key": "",
}

# Fields that are allowed in the public response
_PUBLIC_FIELDS = {"theme", "language", "vault_path", "api_url", "llm_model", "api_key"}

# Allowed theme values
_VALID_THEMES = ("light", "dark", "system")

# Default settings
_DEFAULTS = {
    "theme": "system",
    "language": "en",
    "vault_path": "",
    "api_url": "",
    "llm_model": "gpt-4",
    "api_key": "",
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
        api_key is never returned in plaintext; api_key_set indicates presence.
    """
    result = {}
    for k in _PUBLIC_FIELDS:
        if k == "api_key":
            continue
        result[k] = _settings_cache.get(k, _DEFAULTS.get(k, ""))
    result["api_key_set"] = bool(_settings_cache.get("api_key", ""))
    return result


def get_vault_path() -> Optional[str]:
    """Return the current vault_path from settings.

    Returns:
        Vault path string or None if not configured.
    """
    path = _settings_cache.get("vault_path", "")
    return path if path else None


# Callback list for vault_path change notifications
_vault_change_callbacks: list[Callable[[str | None], None]] = []


def register_vault_change_callback(callback: Callable[[str | None], None]) -> None:
    """Register a callback to be called when vault_path changes.

    Args:
        callback: Callable that takes the new vault_path (str or None) as argument.
    """
    if callback not in _vault_change_callbacks:
        _vault_change_callbacks.append(callback)


# ==============================================================================
# Response / Request Models
# ==============================================================================


class SettingsResponse(BaseModel):
    """Response model for settings."""

    theme: str = "system"
    language: str = "en"
    vault_path: str = ""
    api_url: str = ""
    llm_model: str = "gpt-4"
    api_key_set: bool = False


class SettingsUpdateRequest(BaseModel):
    """Request model for partial settings update.

    All fields are optional. Only provided fields will be updated.
    """

    theme: Optional[str] = None
    language: Optional[str] = None
    vault_path: Optional[str] = None
    api_url: Optional[str] = None
    llm_model: Optional[str] = None
    api_key: Optional[str] = None

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
        """Validate vault_path has no path traversal."""
        if v is not None:
            if ".." in v:
                raise ValueError("Vault path must not contain '..'")
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


def _get_api_key() -> Optional[str]:
    """Return the stored API key (for backend use only)."""
    return _settings_cache.get("api_key") or None


def get_llm_settings() -> dict[str, str]:
    """Return the stored LLM settings for backend request construction."""
    return {
        "api_url": (_settings_cache.get("api_url") or "").strip(),
        "llm_model": (_settings_cache.get("llm_model") or _DEFAULTS["llm_model"]).strip(),
        "api_key": (_settings_cache.get("api_key") or "").strip(),
    }


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

        # Notify listeners if vault_path changed
        if "vault_path" in update_data:
            new_vault = update_data["vault_path"] or None
            for cb in _vault_change_callbacks:
                try:
                    cb(new_vault)
                except Exception as exc:
                    logger.warning("Vault change callback error: %s", exc)

    public = _get_public_settings()
    return SettingsResponse(**public)
