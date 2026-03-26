"""Admin configuration API — read and update runtime API keys.

Provides two endpoints:
  GET  /api/admin/config  — return which keys are configured (never exposes values)
  POST /api/admin/config  — write new key values into the .env file
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

# .env lives in the backend directory (same dir as langgraph.json)
_ENV_PATH = Path(__file__).parents[3] / ".env"


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_env() -> dict[str, str]:
    """Parse .env into a key→value dict (preserves order, skips comments)."""
    env: dict[str, str] = {}
    if not _ENV_PATH.exists():
        return env
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def _save_env(env: dict[str, str]) -> None:
    """Write key→value pairs back to .env, preserving existing comments/order."""
    lines: list[str] = []

    # Re-read original lines to preserve comments and ordering
    original: list[str] = []
    if _ENV_PATH.exists():
        original = _ENV_PATH.read_text(encoding="utf-8").splitlines()

    written_keys: set[str] = set()
    for line in original:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.partition("=")[0].strip()
            if key in env:
                lines.append(f"{key}={env[key]}")
                written_keys.add(key)
            else:
                lines.append(line)
        else:
            lines.append(line)

    # Append any new keys not present in the original file
    for key, value in env.items():
        if key not in written_keys:
            lines.append(f"{key}={value}")

    _ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    _ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("[Admin] .env updated at %s", _ENV_PATH)


def _mask(value: str) -> str:
    """Return last 4 chars with rest masked, e.g. '****dc9'."""
    if not value:
        return ""
    visible = min(4, len(value))
    return "*" * (len(value) - visible) + value[-visible:]


def _is_set(env: dict[str, str], key: str) -> bool:
    return bool(env.get(key, os.environ.get(key, "")).strip())


def _get_masked(env: dict[str, str], key: str) -> str:
    val = env.get(key, os.environ.get(key, ""))
    return _mask(val) if val else ""


# ── Pydantic models ───────────────────────────────────────────────────────────

class AdminConfigStatus(BaseModel):
    deepseek_api_key_set: bool
    deepseek_api_key_hint: str
    telegram_bot_token_set: bool
    telegram_bot_token_hint: str
    tavily_api_key_set: bool
    tavily_api_key_hint: str


class AdminConfigUpdate(BaseModel):
    deepseek_api_key: str | None = None
    telegram_bot_token: str | None = None
    tavily_api_key: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/config", summary="Get admin config status (masked)")
async def get_admin_config() -> AdminConfigStatus:
    """Return which API keys are configured.

    Values are never returned in full — only a masked hint (last 4 chars).
    """
    env = _load_env()
    return AdminConfigStatus(
        deepseek_api_key_set=_is_set(env, "DEEPSEEK_API_KEY"),
        deepseek_api_key_hint=_get_masked(env, "DEEPSEEK_API_KEY"),
        telegram_bot_token_set=_is_set(env, "TELEGRAM_BOT_TOKEN"),
        telegram_bot_token_hint=_get_masked(env, "TELEGRAM_BOT_TOKEN"),
        tavily_api_key_set=_is_set(env, "TAVILY_API_KEY"),
        tavily_api_key_hint=_get_masked(env, "TAVILY_API_KEY"),
    )


@router.post("/config", summary="Save API keys to .env")
async def update_admin_config(request: AdminConfigUpdate) -> dict:
    """Write provided API keys to the .env file.

    Only non-None fields are updated; existing values are preserved.
    Empty strings clear the key.
    """
    env = _load_env()
    updated: list[str] = []

    if request.deepseek_api_key is not None:
        env["DEEPSEEK_API_KEY"] = request.deepseek_api_key.strip()
        updated.append("DEEPSEEK_API_KEY")

    if request.telegram_bot_token is not None:
        env["TELEGRAM_BOT_TOKEN"] = request.telegram_bot_token.strip()
        updated.append("TELEGRAM_BOT_TOKEN")

    if request.tavily_api_key is not None:
        env["TAVILY_API_KEY"] = request.tavily_api_key.strip()
        updated.append("TAVILY_API_KEY")

    if not updated:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    try:
        _save_env(env)
    except OSError as exc:
        logger.exception("[Admin] Failed to write .env")
        raise HTTPException(status_code=500, detail=f"Failed to save config: {exc}") from exc

    logger.info("[Admin] Updated keys: %s", updated)
    return {"success": True, "updated": updated}
