from datetime import datetime, timezone
from enum import StrEnum
from pydantic import BaseModel, Field, HttpUrl
from typing import Any
import uuid

def uid() -> str:
    return str(uuid.uuid4())

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Asset(BaseModel):
    id: str = Field(default_factory=uid)
    kind: str
    value: str
    source: str = "manual"
    notes: str = ""
    created_at: str = Field(default_factory=now_iso)

class Endpoint(BaseModel):
    id: str = Field(default_factory=uid)
    method: str
    url: str
    source: str = "manual"
    notes: str = ""
    created_at: str = Field(default_factory=now_iso)

class Finding(BaseModel):
    id: str = Field(default_factory=uid)
    title: str
    severity: Severity = Severity.INFO
    status: str = "open"
    description: str
    impact: str = ""
    recommendation: str = ""
    asset_id: str | None = None
    created_at: str = Field(default_factory=now_iso)

class Evidence(BaseModel):
    id: str = Field(default_factory=uid)
    finding_id: str
    file_path: str
    description: str = ""
    sha256: str
    created_at: str = Field(default_factory=now_iso)

class ImportedRecord(BaseModel):
    record_type: str
    payload: dict[str, Any]
