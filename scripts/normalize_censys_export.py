from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MAX_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 10_000
SAFE_FIELDS = {
    "ip", "ip_address", "hostname", "host", "domain", "port", "protocol",
    "service_name", "issuer", "validity", "asn", "autonomous_system",
}


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError(f"Input must be a local file no larger than {MAX_BYTES} bytes.")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("results", "result", "hosts", "assets", "records"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
            else:
                data = [data]
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError("JSON export must contain an object or array of objects.")
        records = data
    elif path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as file:
            records = list(csv.DictReader(file))
    else:
        raise ValueError("Only local .json and .csv files are supported.")
    if len(records) > MAX_RECORDS:
        raise ValueError(f"Import exceeds the {MAX_RECORDS} record limit.")
    return records


def normalize_records(records: list[dict[str, Any]], source_reference: str, file_digest: str) -> list[dict]:
    observations = []
    collected_at = datetime.now(UTC).isoformat()
    for record in records:
        lowered = {str(key).strip().lower().replace(" ", "_"): value for key, value in record.items()}
        asset = None
        category = ""
        for key in ("ip", "ip_address"):
            candidate = lowered.get(key)
            if isinstance(candidate, str):
                try:
                    asset = str(ipaddress.ip_address(candidate.strip()))
                    category = "ip_address"
                    break
                except ValueError:
                    continue
        if asset is None:
            for key in ("domain", "hostname", "host"):
                candidate = lowered.get(key)
                if isinstance(candidate, str) and valid_domain(candidate):
                    asset = candidate.strip().lower().rstrip(".")
                    category = "domain"
                    break
        if asset is None:
            continue
        details = {
            key: value
            for key, value in lowered.items()
            if key in SAFE_FIELDS and isinstance(value, (str, int, float, bool)) and len(str(value)) <= 500
        }
        observations.append(
            {
                "category": category,
                "asset": asset,
                "source": "censys_manual_export",
                "source_reference": source_reference,
                "first_observed_at": collected_at,
                "last_observed_at": collected_at,
                "collected_at": collected_at,
                "confidence": "low",
                "verification_status": "requires_authorization" if category == "ip_address" else "candidate",
                "evidence_reference": f"sha256:{file_digest}",
                "details": details,
            }
        )
    return observations


def valid_domain(value: str) -> bool:
    normalized = value.strip().lower().rstrip(".")
    labels = normalized.split(".")
    return len(normalized) <= 253 and len(labels) >= 2 and all(
        DOMAIN_LABEL.fullmatch(label) for label in labels
    )


def default_output_path(target: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", target):
        raise ValueError("Target name must be a simple folder name.")
    return Path("targets") / target / "data" / "censys-normalized.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize an operator-supplied local Censys export; no API or target access."
    )
    parser.add_argument("--target", required=True, help="Target folder name, e.g. fbsu.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output override; defaults to workspace/<target>/data/censys-normalized.json.",
    )
    parser.add_argument(
        "--source-reference",
        required=True,
        help="Original source/search reference for the imported export.",
    )
    args = parser.parse_args()
    try:
        default_path = default_output_path(args.target)
        output_path = args.output or default_path
        records = load_records(args.input)
        digest = hashlib.sha256(args.input.read_bytes()).hexdigest()
        observations = normalize_records(records, args.source_reference, digest)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({"observations": observations}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(observations)} normalized record(s) to {output_path}")
    print("Imported IP addresses remain requires_authorization; no scope was changed.")
    return 0


DOMAIN_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


if __name__ == "__main__":
    raise SystemExit(main())
