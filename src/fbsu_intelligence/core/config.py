from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_ROOT = PROJECT_ROOT / "config"


def workspace_root() -> Path:
    return Path(os.environ.get("FBSU_INTEL_HOME", str(PROJECT_ROOT / "workspace"))).expanduser().resolve()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Unable to read configuration file {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TypeError(f"Expected a YAML mapping in {path}.")
    return value


def load_config(name: str) -> dict[str, Any]:
    return load_yaml(CONFIG_ROOT / name)
