from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from fbsu_intelligence.core.config import CONFIG_ROOT, load_config, workspace_root
from fbsu_intelligence.core.database import Repository
from fbsu_intelligence.core.models import Domain, PublicMetadataResource

DATA_DIRS = (
    "assets", "domains", "dns", "certificates", "technologies", "dependencies",
    "public-metadata", "applications", "third-party", "evidence", "exports",
    "logs", "reports",
)


def fbsu_path() -> Path:
    return workspace_root() / "fbsu"


def get_repository() -> Repository:
    root = fbsu_path()
    if not root.exists():
        raise FileNotFoundError("FBSU workspace is not initialized. Run 'fbsu-intel init'.")
    return Repository(root / "intelligence.sqlite3")


def initialize_workspace() -> Path:
    root = fbsu_path()
    if root.exists() and (root / "engagement.yaml").exists():
        raise FileExistsError(f"FBSU workspace already exists: {root}")
    root.mkdir(parents=True, exist_ok=True)
    for folder in DATA_DIRS:
        (root / folder).mkdir(exist_ok=True)
    for config_name in ("targets.yaml", "sources.yaml", "exclusions.yaml", "collection-policy.yaml"):
        shutil.copy2(CONFIG_ROOT / config_name, root / config_name)
    engagement = load_config("settings.yaml").get("engagement", {})
    (root / "engagement.yaml").write_text(
        yaml.safe_dump(engagement, sort_keys=False), encoding="utf-8"
    )
    repository = Repository(root / "intelligence.sqlite3")
    target_data = load_config("targets.yaml")
    seen: set[str] = set()
    for name in target_data.get("domains", []):
        domain = Domain(name=name, source_reference="config/targets.yaml")
        if domain.name in seen:
            continue
        seen.add(domain.name)
        repository.insert("domains", domain.model_dump(mode="json"))
    for entry in load_config("sources.yaml").get("public_metadata_references", []):
        resource = PublicMetadataResource(url=entry["url"], source_url=entry["url"], notes=entry.get("notes", ""))
        repository.insert("metadata_resources", resource.model_dump())
    return root


def status() -> dict[str, Any]:
    root = fbsu_path()
    if not root.exists():
        return {"initialized": False, "path": str(root), "domains": 0, "observations": 0}
    repository = Repository(root / "intelligence.sqlite3")
    return {
        "initialized": True,
        "path": str(root),
        "domains": len(repository.list("domains")),
        "observations": len(repository.list("observations")),
        "metadata_references": len(repository.list("metadata_resources")),
    }
