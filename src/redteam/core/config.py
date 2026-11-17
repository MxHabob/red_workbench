from pathlib import Path
import os
import yaml

def workspace_root() -> Path:
    return Path(os.environ.get("RTW_HOME", "./workspace")).expanduser().resolve()

def load_settings(project_root: Path | None = None) -> dict:
    path = Path("config/settings.yaml")
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    else:
        data = {}
    data["workspace_dir"] = os.environ.get("RTW_HOME", data.get("workspace_dir", "./workspace"))
    return data
