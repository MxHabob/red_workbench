import json
from pathlib import Path
from redteam.core.workspace import engagement_path, get_db

def export_json(name: str) -> Path:
    root = engagement_path(name)
    payload = {table: get_db(name).rows(table) for table in ("assets", "endpoints", "findings", "evidence")}
    out = root / "exports" / "engagement-export.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out

def generate_report(name: str) -> Path:
    root = engagement_path(name)
    db = get_db(name)
    assets, endpoints = db.rows("assets"), db.rows("endpoints")
    findings, evidence = db.rows("findings"), db.rows("evidence")
    lines = [
        f"# Assessment report: {name}", "",
        "> This report is generated from operator-supplied records. Confirm authorization and evidence before distribution.", "",
        "## Summary", "",
        f"- Assets: {len(assets)}", f"- Endpoints: {len(endpoints)}",
        f"- Findings: {len(findings)}", f"- Evidence records: {len(evidence)}", "",
        "## Findings", ""
    ]
    if not findings:
        lines.append("No findings have been recorded.")
    for item in findings:
        lines += [f"### {item['title']}", "", f"- ID: `{item['id']}`",
                  f"- Severity: **{item['severity']}**", f"- Status: {item['status']}", "",
                  item["description"], ""]
        if item["impact"]: lines += ["**Impact**", "", item["impact"], ""]
        if item["recommendation"]: lines += ["**Recommendation**", "", item["recommendation"], ""]
    lines += ["## Asset inventory", ""]
    lines += [f"- `{x['kind']}` — `{x['value']}` ({x['source']})" for x in assets] or ["No assets recorded."]
    lines += ["", "## Endpoint inventory", ""]
    lines += [f"- `{x['method']}` — `{x['url']}`" for x in endpoints] or ["No endpoints recorded."]
    out = root / "reports" / "assessment-report.md"
    out.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    return out
