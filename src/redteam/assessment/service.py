from pathlib import Path
import hashlib
from redteam.core.models import Finding, Evidence, Severity
from redteam.core.workspace import get_db, engagement_path

def add_finding(name: str, title: str, severity: str, description: str,
                impact: str = "", recommendation: str = "", asset_id: str | None = None):
    item = Finding(title=title, severity=Severity(severity), description=description,
                   impact=impact, recommendation=recommendation, asset_id=asset_id)
    get_db(name).insert("findings", item.model_dump())
    return item

def add_evidence(name: str, finding_id: str, file_path: str, description: str = ""):
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    item = Evidence(finding_id=finding_id, file_path=str(path),
                    description=description, sha256=digest)
    get_db(name).insert("evidence", item.model_dump())
    return item
