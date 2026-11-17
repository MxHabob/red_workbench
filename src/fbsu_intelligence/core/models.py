from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def new_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class VerificationStatus(StrEnum):
    DISCOVERED = "discovered"
    CANDIDATE = "candidate"
    OBSERVED = "observed"
    VERIFIED = "verified"
    EXCLUDED = "excluded"
    REQUIRES_AUTHORIZATION = "requires_authorization"


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Organization(BaseModel):
    name: str
    primary_domain: str


class Engagement(BaseModel):
    id: str = Field(default_factory=new_id)
    organization: str = "FBSU"
    name: str = "FBSU Public-Source Asset Intelligence"
    status: str = "planning"
    authorization_reference: str = ""
    created_at: str = Field(default_factory=utc_now)


class Domain(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    status: VerificationStatus = VerificationStatus.CANDIDATE
    source: str = "operator_supplied"
    source_reference: str = ""
    added_at: str = Field(default_factory=utc_now)

    @field_validator("name")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        normalized = value.strip().lower().rstrip(".")
        if not normalized or len(normalized) > 253:
            raise ValueError("Domain must contain between 1 and 253 characters.")
        labels = normalized.split(".")
        if len(labels) < 2 or any(
            not label
            or len(label) > 63
            or label.startswith("-")
            or label.endswith("-")
            or not all(char.isalnum() or char == "-" for char in label)
            for label in labels
        ):
            raise ValueError(f"Invalid domain name: {value}")
        return normalized


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=new_id)
    category: str
    asset: str
    source: str
    source_reference: str
    first_observed_at: str = Field(default_factory=utc_now)
    last_observed_at: str = Field(default_factory=utc_now)
    collected_at: str = Field(default_factory=utc_now)
    confidence: Confidence = Confidence.LOW
    verification_status: VerificationStatus = VerificationStatus.OBSERVED
    evidence_reference: str = ""
    details: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_timestamps(self) -> Observation:
        try:
            first = datetime.fromisoformat(self.first_observed_at.replace("Z", "+00:00"))
            last = datetime.fromisoformat(self.last_observed_at.replace("Z", "+00:00"))
            collected = datetime.fromisoformat(self.collected_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Observation timestamps must be ISO-8601 values.") from exc
        if any(not stamp.tzinfo for stamp in (first, last, collected)):
            raise ValueError("Observation timestamps must include a timezone.")
        if first > last:
            raise ValueError("first_observed_at cannot be later than last_observed_at.")
        return self


class PublicMetadataResource(BaseModel):
    id: str = Field(default_factory=new_id)
    url: str
    category: str = "public_metadata"
    status_code: int | None = Field(default=None, ge=100, le=599)
    availability: str = "not_checked"
    content_type: str = ""
    response_size: int | None = Field(default=None, ge=0)
    observed_at: str = Field(default_factory=utc_now)
    source_url: str
    notes: str = ""

    @field_validator("url", "source_url")
    @classmethod
    def require_http_reference(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("References must be absolute HTTP(S) URLs.")
        return value


class IntelligenceSource(BaseModel):
    name: str
    kind: str
    reference: str
    reliability: str = "unassessed"
    access_mode: str = "manual_or_import_only"


class CollectionEvent(BaseModel):
    id: str = Field(default_factory=new_id)
    stage: str
    status: str
    started_at: str = Field(default_factory=utc_now)
    completed_at: str = Field(default_factory=utc_now)
    source: str = ""
    message: str = ""


class ImportedObservation(BaseModel):
    """Allow-listed fields extracted from an offline Censys export."""

    asset: str
    category: str
    source_reference: str
    details: dict[str, str | int | float | bool] = Field(default_factory=dict)
