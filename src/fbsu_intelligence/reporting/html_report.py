from __future__ import annotations

import html
from pathlib import Path

from fbsu_intelligence.core.workspace import fbsu_path
from fbsu_intelligence.reporting.report_generator import generate_markdown


def generate_html() -> Path:
    markdown_path = generate_markdown()
    rows = []
    for raw_line in markdown_path.read_text(encoding="utf-8").splitlines():
        line = html.escape(raw_line)
        if raw_line.startswith("# "):
            rows.append(f"<h1>{html.escape(raw_line[2:])}</h1>")
        elif raw_line.startswith("## "):
            rows.append(f"<h2>{html.escape(raw_line[3:])}</h2>")
        elif raw_line.startswith("### "):
            rows.append(f"<h3>{html.escape(raw_line[4:])}</h3>")
        elif raw_line.startswith("- "):
            rows.append(f"<p>{line}</p>")
        elif raw_line.startswith("|"):
            rows.append(f"<pre>{line}</pre>")
        elif raw_line.startswith("> "):
            rows.append(f"<blockquote>{html.escape(raw_line[2:])}</blockquote>")
        elif raw_line:
            rows.append(f"<p>{line}</p>")
    content = "\n".join(rows)
    document = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>FBSU Public-Source Asset Intelligence</title>"
        "<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1000px;margin:3rem auto;padding:0 1rem}"
        "h1,h2{color:#16324f}pre{overflow-wrap:anywhere;white-space:pre-wrap;background:#f4f6f8;padding:.5rem}"
        "blockquote{border-left:4px solid #d99000;padding-left:1rem}</style></head>"
        f"<body>{content}</body></html>"
    )
    target = fbsu_path() / "reports" / "fbsu-intelligence.html"
    target.write_text(document, encoding="utf-8")
    return target
