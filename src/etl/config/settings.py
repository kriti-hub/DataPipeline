"""ETL pipeline settings — loads pipeline.yaml with env-var interpolation.

Usage::

    from config.settings import get_settings
    cfg = get_settings()
    print(cfg["source"]["base_url"])
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml

_ENV_VAR_RE = re.compile(r"\$\{(\w+)\}")

# Resolve paths relative to this file so they work both locally
# (running from repo root via ``python -m src.etl.pipeline``) and when
# deployed to Cloud Functions (where ``src/etl/`` is the source root).
_CONFIG_DIR = Path(__file__).resolve().parent          # src/etl/config/
_ETL_ROOT = _CONFIG_DIR.parent                         # src/etl/
_REPO_ROOT = _ETL_ROOT.parents[1]                      # repo root

_PIPELINE_YAML = _CONFIG_DIR / "pipeline.yaml"

# quality_rules.yaml lives at <repo>/config/ in development.
# For Cloud Functions deployment, copy it into src/etl/config/ (the deploy
# script handles this).  We check the local copy first, then fall back to
# the repo-root location.
_QUALITY_RULES_LOCAL = _CONFIG_DIR / "quality_rules.yaml"
_QUALITY_RULES_REPO = _REPO_ROOT / "config" / "quality_rules.yaml"
_QUALITY_RULES_YAML = (
    _QUALITY_RULES_LOCAL if _QUALITY_RULES_LOCAL.exists() else _QUALITY_RULES_REPO
)


def _interpolate(value: Any) -> Any:
    """Recursively replace ``${VAR}`` placeholders with env-var values."""
    if isinstance(value, str):
        def _replacer(match: re.Match) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        return _ENV_VAR_RE.sub(_replacer, value)
    if isinstance(value, dict):
        return {k: _interpolate(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_interpolate(v) for v in value]
    return value


def load_yaml(path: Path) -> dict:
    """Read a YAML file, interpolate env vars, and return a dict.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed and interpolated configuration dictionary.
    """
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return _interpolate(raw)


_settings_cache: dict | None = None


def get_settings() -> dict:
    """Return the cached pipeline configuration.

    Returns:
        Fully-resolved pipeline config dict.
    """
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = load_yaml(_PIPELINE_YAML)
    return _settings_cache


def get_quality_rules() -> dict:
    """Load the externalized data quality rules.

    Returns:
        Parsed quality_rules.yaml as a dict.
    """
    return load_yaml(_QUALITY_RULES_YAML)


def get_source_config() -> dict:
    """Shortcut for ``get_settings()["source"]``."""
    return get_settings()["source"]


def get_destination_config() -> dict:
    """Shortcut for ``get_settings()["destination"]``."""
    return get_settings()["destination"]
