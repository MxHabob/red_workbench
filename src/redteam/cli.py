from pathlib import Path
import typer
from rich import print
from rich.table import Table
from redteam.core.workspace import create_engagement, engagement_path, get_db
from redteam.inventory.service import add_asset, add_endpoint
from redteam.assessment.service import add_finding, add_evidence
from redteam.reporting.service import generate_report, export_json

app = typer.Typer(help="RedTeam Workbench — local-first assessment workspace.")
scope_app = typer.Typer(help="Manage the written engagement scope.")
app.add_typer(scope_app, name="scope")

@app.command()
def init(name: str):
    """Create a new engagement workspace."""
    try:
        path = create_engagement(name)
        print(f"[green]Created[/green] {path}")
    except (ValueError, FileExistsError) as exc:
        raise typer.BadParameter(str(exc))

@app.command("list")
def list_engagements():
    """List local engagements."""
    from redteam.core.config import workspace_root
    base = workspace_root()
    table = Table("Engagement", "Status")
    if base.exists():
        for p in sorted(base.iterdir()):
            if p.is_dir() and (p / "engagement.yaml").exists():
                table.add_row(p.name, "local")
    print(table)

@app.command()
def show(name: str):
    """Show engagement inventory counts."""
    db = get_db(name)
    print(f"[bold]{name}[/bold]")
    for table in ("assets", "endpoints", "findings", "evidence"):
        print(f"{table}: {len(db.rows(table))}")

@app.command()
def asset(name: str, kind: str = typer.Option(...), value: str = typer.Option(...),
          source: str = "manual", notes: str = ""):
    item = add_asset(name, kind, value, source, notes)
    print(f"[green]Asset added:[/green] {item.id}")

@app.command()
def endpoint(name: str, method: str = "GET", url: str = typer.Option(...), notes: str = ""):
    try:
        item = add_endpoint(name, method, url, notes=notes)
        print(f"[green]Endpoint recorded:[/green] {item.id}")
    except ValueError as exc:
        raise typer.BadParameter(str(exc))

@app.command()
def finding(name: str, title: str, severity: str = "info", description: str = "",
            impact: str = "", recommendation: str = ""):
    item = add_finding(name, title, severity, description, impact, recommendation)
    print(f"[green]Finding recorded:[/green] {item.id}")

@app.command()
def evidence(name: str, finding_id: str, file: str, description: str = ""):
    item = add_evidence(name, finding_id, file, description)
    print(f"[green]Evidence recorded; SHA-256:[/green] {item.sha256}")

@scope_app.command("show")
def scope_show(name: str):
    import yaml
    path = engagement_path(name) / "scope" / "scope.yaml"
    print(yaml.safe_load(path.read_text(encoding="utf-8")))

@scope_app.command("add-domain")
def scope_add_domain(name: str, domain: str):
    import yaml
    path = engagement_path(name) / "scope" / "scope.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    domains = data.setdefault("scope", {}).setdefault("domains", [])
    if domain not in domains: domains.append(domain.lower().strip("."))
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    print(f"[green]Added in-scope domain:[/green] {domain}")

@app.command()
def report(name: str):
    print(f"[green]Report:[/green] {generate_report(name)}")

@app.command()
def export(name: str):
    print(f"[green]Export:[/green] {export_json(name)}")

@app.command("import-json")
def import_json(name: str, file: str):
    """Import asset records from a local JSON file; no network access is performed."""
    import json
    from redteam.core.models import Asset
    data = json.loads(Path(file).read_text(encoding="utf-8"))
    records = data if isinstance(data, list) else [data]
    count = 0
    for record in records:
        item = Asset(**record)
        get_db(name).insert("assets", item.model_dump())
        count += 1
    print(f"[green]Imported {count} asset record(s).[/green]")

if __name__ == "__main__":
    app()
