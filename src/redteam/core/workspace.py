from pathlib import Path
import yaml
from redteam.core.config import workspace_root
from redteam.core.database import Database

def engagement_path(name: str) -> Path:
    if not name or any(c in name for c in ("/", "\\", "..")):
        raise ValueError("Engagement name must be a simple folder name")
    return workspace_root() / name

def create_engagement(name: str) -> Path:
    root = engagement_path(name)
    if root.exists():
        raise FileExistsError(f"Engagement already exists: {name}")
    for folder in ("authorization", "scope", "intelligence", "reconnaissance",
                   "assets", "applications", "api-inventory", "assessment",
                   "simulation", "evidence", "logs", "reports", "exports"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    metadata = {
        "name": name, "status": "planning", "created_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "data_classification": "synthetic_or_operator_supplied"
    }
    (root / "engagement.yaml").write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
    scope = {
        "engagement": {"name": name, "authorization_reference": ""},
        "scope": {"domains": [], "ip_ranges": [], "excluded_domains": [], "excluded_ip_ranges": []},
        "notes": "Add only assets explicitly covered by written authorization."
    }
    (root / "scope" / "scope.yaml").write_text(yaml.safe_dump(scope, sort_keys=False), encoding="utf-8")
    Database(root / "engagement.sqlite3")
    return root

def get_db(name: str) -> Database:
    root = engagement_path(name)
    if not root.exists():
        raise FileNotFoundError(f"Unknown engagement: {name}. Run 'rtw init {name}' first.")
    return Database(root / "engagement.sqlite3")
