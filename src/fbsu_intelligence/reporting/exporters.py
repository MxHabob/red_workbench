from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from fbsu_intelligence.core.workspace import fbsu_path, get_repository


def export_payload() -> dict[str, Any]:
    return {
        "organization": {"name": "FBSU", "primary_domain": "fbsu.edu.sa"},
        "scope_notice": "Candidate inventory only; no ownership or authorization is implied.",
        "domains": get_repository().list("domains"),
        "observations": get_repository().list("observations"),
        "public_metadata_resources": get_repository().list("metadata_resources"),
        "collection_events": get_repository().list("collection_events"),
    }


def export_json() -> Path:
    payload = export_payload()
    schema_path = Path(__file__).resolve().parents[3] / "schemas" / "fbsu-export.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate(instance=payload, schema=schema)
    target = fbsu_path() / "exports" / "fbsu-intelligence.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def export_csv() -> Path:
    target = fbsu_path() / "exports" / "observations.csv"
    columns = (
        "id", "category", "asset", "source", "source_reference", "first_observed_at",
        "last_observed_at", "collected_at", "confidence", "verification_status",
        "evidence_reference", "details",
    )
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in get_repository().list("observations"):
            writer.writerow({**row, "details": json.dumps(row["details"], ensure_ascii=True)})
    return target
