from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from fbsu_intelligence.core.config import load_config
from fbsu_intelligence.core.models import Confidence, Observation, VerificationStatus, utc_now
from fbsu_intelligence.core.workspace import get_repository

MAX_IMPORT_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 10_000
SAFE_FIELDS = {
    "ip", "ip_address", "hostname", "host", "domain", "port", "protocol",
    "service", "service_name", "tls", "certificate", "issuer", "subject",
    "validity", "location", "asn", "autonomous_system",
}
SECRET_KEY = re.compile(r"(password|cookie|token|secret|credential|private|authorization|email)", re.I)
IP_PATTERN = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$|^[0-9a-fA-F:]{3,}$")


def _safe_details(record: dict[str, Any]) -> dict[str, str | int | float | bool]:
    result: dict[str, str | int | float | bool] = {}
    for key, value in record.items():
        normalized_key = key.strip().lower().replace(" ", "_")
        if normalized_key not in SAFE_FIELDS or SECRET_KEY.search(normalized_key):
            continue
        if isinstance(value, (str, int, float, bool)) and len(str(value)) <= 500:
            result[normalized_key] = value
    return result


def _records_from_json(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        for key in ("result", "results", "hosts", "assets", "records"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            data = [data]
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Censys JSON must contain an object or an array of objects.")
    if len(data) > MAX_RECORDS:
        raise ValueError(f"Import exceeds the {MAX_RECORDS} record limit.")
    return data


def _asset_value(record: dict[str, Any]) -> tuple[str, str] | None:
    lowered = {str(key).strip().lower().replace(" ", "_"): value for key, value in record.items()}
    for key in ("ip", "ip_address"):
        value = lowered.get(key)
        if isinstance(value, str) and IP_PATTERN.fullmatch(value.strip()):
            return "ip_address", value.strip()
    for key in ("domain", "hostname", "host"):
        value = lowered.get(key)
        if isinstance(value, str) and "." in value and len(value) <= 253:
            return "domain", value.strip().lower().rstrip(".")
    return None


def _store_record(record: dict[str, Any], source_reference: str) -> bool:
    asset = _asset_value(record)
    if asset is None:
        return False
    kind, value = asset
    observation = Observation(
        category="censys_" + ("ip" if kind == "ip_address" else "domain"),
        asset=value,
        source="censys_manual_export",
        source_reference=source_reference,
        confidence=Confidence.LOW,
        verification_status=(
            VerificationStatus.REQUIRES_AUTHORIZATION if kind == "ip_address"
            else VerificationStatus.CANDIDATE
        ),
        evidence_reference=source_reference,
        details=_safe_details(record),
    )
    get_repository().insert(
        "observations",
        {
            **observation.model_dump(mode="json", exclude={"details"}),
            "details_json": json.dumps(observation.details, ensure_ascii=True),
        },
    )
    return True


def import_censys_file(path: Path) -> int:
    settings = load_config("settings.yaml")
    limit = min(int(settings.get("max_import_bytes", MAX_IMPORT_BYTES)), MAX_IMPORT_BYTES)
    if not path.is_file():
        raise ValueError(f"Import file does not exist: {path}")
    if path.stat().st_size > limit:
        raise ValueError(f"Import file exceeds the configured {limit}-byte limit.")
    source_reference = str(path.resolve())
    if path.suffix.lower() == ".json":
        records = _records_from_json(json.loads(path.read_text(encoding="utf-8")))
    elif path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            records = list(csv.DictReader(handle))
        if len(records) > MAX_RECORDS:
            raise ValueError(f"Import exceeds the {MAX_RECORDS} record limit.")
    else:
        raise ValueError("Censys import accepts local .json or .csv exports only.")
    return sum(_store_record(record, source_reference) for record in records)
