from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fbsu_intelligence.core.workspace import fbsu_path, get_repository


def generate_markdown() -> Path:
    repository = get_repository()
    domains = repository.list("domains")
    observations = repository.list("observations")
    metadata = repository.list("metadata_resources")
    lines = [
        "# FBSU Public-Source Asset Intelligence",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "> This is a local inventory of supplied references and imported observations. "
        "It is not evidence that any asset is owned, reachable, or authorized for testing.",
        "",
        "## Executive summary",
        "",
        f"- Candidate domains: {len(domains)}",
        f"- Imported observations: {len(observations)}",
        f"- Public metadata references: {len(metadata)}",
        "- Network collection performed by this workspace: **No**",
        "",
        "## Initial target inventory",
        "",
    ]
    for domain in domains:
        lines.append(
            f"- `{domain['name']}` — **{domain['status']}**; source: `{domain['source_reference']}`"
        )
    if not domains:
        lines.append("No candidate domains are registered.")
    lines += ["", "## Intelligence observations", ""]
    if observations:
        for item in observations:
            lines += [
                f"### {item['category']}: `{item['asset']}`",
                "",
                f"- Status: **{item['verification_status']}**",
                f"- Confidence: **{item['confidence']}**",
                f"- Source: `{item['source']}`",
                f"- Source reference: `{item['source_reference']}`",
                f"- First/last observed: {item['first_observed_at']} / {item['last_observed_at']}",
                f"- Collected: {item['collected_at']}",
                f"- Evidence reference: `{item['evidence_reference'] or 'not supplied'}`",
                f"- Normalized details: `{item['details']}`",
                "",
            ]
    else:
        lines.append("No imported or operator-recorded observations are present.")
    lines += [
        "",
        "## Public metadata references",
        "",
        "| Reference | Availability | HTTP status | Content type | Response size | Observed | Source |",
        "|---|---|---:|---|---:|---|---|",
    ]
    for item in metadata:
        status = item["status_code"] if item["status_code"] is not None else "not recorded"
        size = item["response_size"] if item["response_size"] is not None else "not recorded"
        lines.append(
            f"| {item['url']} | {item['availability']} | {status} | {item['content_type'] or 'not recorded'} "
            f"| {size} | {item['observed_at']} | {item['source_url']} |"
        )
    lines += [
        "",
        "## Confidence, verification, and limitations",
        "",
        "- Supplied domains remain **candidates**; syntax validation does not establish ownership.",
        "- Imported Censys data is third-party observation, not an independently verified fact.",
        "- IP observations are marked `requires_authorization` and never enter domain scope automatically.",
        "- Availability fields are `not_checked` until manually recorded from an authorized process.",
        "- No target URLs are fetched, no DNS queries are run, and no active testing is performed.",
        "- Third-party services and newly discovered subdomains require ownership and written authorization review.",
        "- The workspace stores normalized metadata only; do not import secrets, credentials, cookies, tokens, or personal records.",
        "",
        "## Items requiring review",
        "",
        "- Verify ownership and engagement scope for every candidate domain.",
        "- Treat supplied IP-based references and all discovered IP addresses as out of scope until expressly authorized.",
        "- Obtain written authorization before any collection beyond local imports and operator-entered records.",
        "",
    ]
    target = fbsu_path() / "reports" / "fbsu-intelligence.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target
