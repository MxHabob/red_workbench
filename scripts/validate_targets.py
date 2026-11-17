from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

DOMAIN_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def validate_target_data(data: dict) -> list[str]:
    domains = data.get("domains")
    if not isinstance(domains, list) or not domains:
        return ["domains must be a non-empty list"]
    errors = []
    seen = set()
    for domain in domains:
        if not isinstance(domain, str):
            errors.append(f"{domain!r}: expected a domain string")
            continue
        normalized = domain.strip().lower().rstrip(".")
        labels = normalized.split(".")
        if len(normalized) > 253 or len(labels) < 2 or not all(DOMAIN_LABEL.fullmatch(x) for x in labels):
            errors.append(f"{domain!r}: invalid domain syntax")
        elif normalized in seen:
            errors.append(f"{domain!r}: duplicate domain")
        seen.add(normalized)
    primary = data.get("primary_domain")
    if primary and primary.strip().lower().rstrip(".") not in seen:
        errors.append("primary_domain must appear in domains")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Syntax-check a local target YAML file; no network access.")
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.file.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        parser.error(f"cannot read valid YAML: {exc}")
    if not isinstance(data, dict):
        parser.error("target file must contain a YAML mapping")
    errors = validate_target_data(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Syntax valid: {len(data['domains'])} candidate domain(s). Ownership is not verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
