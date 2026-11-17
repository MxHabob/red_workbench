from __future__ import annotations

from pathlib import Path

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from fbsu_intelligence.core.config import load_config
from fbsu_intelligence.core.models import (
    Confidence,
    Domain,
    Observation,
    PublicMetadataResource,
    VerificationStatus,
)
from fbsu_intelligence.core.workspace import (
    fbsu_path,
    get_repository,
    initialize_workspace,
    status as workspace_status,
)
from fbsu_intelligence.integrations.censys_import import import_censys_file
from fbsu_intelligence.intelligence.source_registry import list_sources
from fbsu_intelligence.reporting.exporters import export_csv, export_json
from fbsu_intelligence.reporting.html_report import generate_html
from fbsu_intelligence.reporting.report_generator import generate_markdown

app = typer.Typer(
    name="fbsu-intel",
    help="FBSU local-first public-source asset intelligence (offline imports only).",
    no_args_is_help=True,
)
targets_app = typer.Typer(help="List supplied target candidates and syntax-check them.")
censys_app = typer.Typer(help="Import manually exported Censys observations; no API calls.")
metadata_app = typer.Typer(help="Review supplied metadata references and record manual results.")
assets_app = typer.Typer(help="List normalized candidate assets.")
domains_app = typer.Typer(help="List candidate domains.")
technologies_app = typer.Typer(help="List technology observations.")
dependencies_app = typer.Typer(help="List dependency observations.")
applications_app = typer.Typer(help="List application observations.")
observations_app = typer.Typer(help="Record and list source-backed observations.")
reports_app = typer.Typer(help="Generate traceable local reports.")
export_app = typer.Typer(help="Export normalized local inventory.")
workspace_app = typer.Typer(help="Show local FBSU workspace state.")
for group, name in (
    (targets_app, "targets"), (censys_app, "censys"), (metadata_app, "metadata"),
    (assets_app, "assets"), (domains_app, "domains"), (technologies_app, "technologies"),
    (dependencies_app, "dependencies"), (applications_app, "applications"),
    (observations_app, "observations"), (reports_app, "report"),
    (export_app, "export"), (workspace_app, "workspace"),
):
    app.add_typer(group, name=name)

console = Console()
CATEGORIES = {
    "domain", "dns_record", "ip_address", "certificate", "technology", "dependency",
    "application", "third_party", "public_metadata", "documented_api",
}


def _repository():
    try:
        return get_repository()
    except (OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc


def _table(title: str, columns: tuple[str, ...], rows: list[dict]) -> None:
    table = Table(title=title)
    for column in columns:
        table.add_column(column.replace("_", " ").title(), overflow="fold")
    for row in rows:
        table.add_row(*(str(row.get(column, "")) for column in columns))
    console.print(table)


@app.command()
def init(force: bool = typer.Option(False, "--force", help="Reuse an existing workspace.")):
    """Initialize workspace and register supplied domains as unverified candidates."""
    try:
        if force and (fbsu_path() / "engagement.yaml").exists():
            console.print(f"[yellow]Workspace already initialized:[/yellow] {fbsu_path()}")
            raise typer.Exit(0)
        path = initialize_workspace()
    except (OSError, ValueError, FileExistsError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Initialized candidate inventory:[/green] {path}")
    console.print("[yellow]No ownership verification, target access, or network collection was performed.[/yellow]")


@targets_app.command("list")
def targets_list():
    """List configured domains without asserting ownership."""
    _table(
        "Supplied target candidates",
        ("name", "status", "source", "source_reference"),
        _repository().list("domains"),
    )


@targets_app.command("verify")
def targets_verify():
    """Validate domain syntax and duplicates only; does not verify ownership or reachability."""
    config = load_config("targets.yaml")
    names = config.get("domains", [])
    errors: list[str] = []
    seen: set[str] = set()
    for name in names:
        try:
            domain = Domain(name=name)
            if domain.name in seen:
                errors.append(f"{domain.name}: duplicate")
            seen.add(domain.name)
        except ValidationError as exc:
            errors.append(f"{name}: {exc.errors()[0]['msg']}")
    if errors:
        for error in errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Syntax valid: {len(seen)} unique domain(s).[/green]")
    console.print("[yellow]Ownership, operational control, and authorization remain unverified.[/yellow]")


@app.command()
def sources():
    """List registered public and imported intelligence sources."""
    _table("Intelligence sources", ("name", "type", "reference", "reliability"), list_sources())


@censys_app.command("import")
def censys_import(file: Path = typer.Argument(..., exists=True, readable=True)):
    """Import a local Censys JSON/CSV export using allow-listed fields only."""
    try:
        count = import_censys_file(file)
    except (OSError, ValueError, UnicodeError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Imported {count} normalized Censys observation(s).[/green]")
    console.print("[yellow]Imported results remain unverified; IP observations require authorization.[/yellow]")


@censys_app.command("status")
def censys_status():
    """Show safe integration status; credentials are not read and no API request is made."""
    console.print("Censys API: [yellow]disabled (passive offline-import mode)[/yellow]")
    console.print("Supported input: local JSON/CSV exports.")
    console.print("Credential variables: not read. No credentials are needed or stored.")


@metadata_app.command("inventory")
def metadata_inventory():
    """List supplied URL references and manually recorded response metadata."""
    _table(
        "Metadata references (not fetched)",
        ("url", "availability", "status_code", "content_type", "response_size", "observed_at"),
        _repository().list("metadata_resources"),
    )


@metadata_app.command("record")
def metadata_record(
    url: str,
    status_code: int | None = typer.Option(None, min=100, max=599),
    content_type: str = "",
    response_size: int | None = typer.Option(None, min=0),
    availability: str = typer.Option("recorded", help="Manual status; e.g. available, unavailable, blocked."),
    source_url: str = typer.Option(..., help="Reference to the operator's authorized evidence/source."),
):
    """Record metadata from an authorized manual review; the CLI does not fetch the URL."""
    repo = _repository()
    known_urls = {item["url"] for item in repo.list("metadata_resources")}
    if url not in known_urls:
        raise typer.BadParameter("Only pre-registered metadata references may be updated.")
    try:
        item = PublicMetadataResource(
            url=url,
            status_code=status_code,
            content_type=content_type,
            response_size=response_size,
            availability=availability,
            source_url=source_url,
            notes="Manually recorded; no collection was performed by this command.",
        )
        repo.insert("metadata_resources", item.model_dump(), replace=True)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print("[green]Manual metadata record saved.[/green]")


@assets_app.command("list")
def assets_list():
    rows = [
        {"kind": "domain", "asset": item["name"], "status": item["status"], "source": item["source"]}
        for item in _repository().list("domains")
    ]
    rows.extend(
        {"kind": item["category"], "asset": item["asset"], "status": item["verification_status"], "source": item["source"]}
        for item in _repository().list("observations")
    )
    _table("Assets", ("kind", "asset", "status", "source"), rows)


@domains_app.command("list")
def domains_list():
    _table("Domains", ("name", "status", "source", "source_reference"), _repository().list("domains"))


def _list_category(category: str) -> None:
    rows = _repository().list("observations")
    _table(
        f"{category.title()} observations",
        ("asset", "verification_status", "confidence", "source", "source_reference"),
        [row for row in rows if row["category"] == category],
    )


@technologies_app.command("list")
def technologies_list():
    _list_category("technology")


@dependencies_app.command("list")
def dependencies_list():
    _list_category("dependency")


@applications_app.command("list")
def applications_list():
    _list_category("application")


@observations_app.command("add")
def observation_add(
    category: str = typer.Option(..., help="One of the documented inventory categories."),
    asset: str = typer.Option(...),
    source: str = typer.Option(...),
    source_reference: str = typer.Option(...),
    status: VerificationStatus = typer.Option(VerificationStatus.OBSERVED),
    confidence: Confidence = typer.Option(Confidence.LOW),
    evidence_reference: str = "",
):
    """Record a source-backed normalized observation; never performs discovery."""
    if category not in CATEGORIES:
        raise typer.BadParameter(f"Unsupported category. Choose: {', '.join(sorted(CATEGORIES))}.")
    try:
        item = Observation(
            category=category,
            asset=asset,
            source=source,
            source_reference=source_reference,
            verification_status=status,
            confidence=confidence,
            evidence_reference=evidence_reference,
        )
        _repository().insert(
            "observations",
            {**item.model_dump(mode="json", exclude={"details"}), "details_json": "{}"},
        )
    except ValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Observation recorded:[/green] {item.id}")


@observations_app.command("list")
def observations_list(category: str = ""):
    rows = _repository().list("observations")
    if category:
        rows = [row for row in rows if row["category"] == category]
    _table(
        "Observations",
        ("category", "asset", "verification_status", "confidence", "source", "source_reference"),
        rows,
    )


@reports_app.command("generate")
def report_generate(format: str = typer.Option("all", help="markdown, html, or all")):
    """Generate evidence-traceable Markdown and HTML reports."""
    if format not in {"markdown", "html", "all"}:
        raise typer.BadParameter("Format must be markdown, html, or all.")
    outputs = []
    if format in {"markdown", "all"}:
        outputs.append(generate_markdown())
    if format in {"html", "all"}:
        outputs.append(generate_html())
    for output in outputs:
        console.print(f"[green]Report:[/green] {output}")


@export_app.command("json")
def export_json_command():
    """Create and JSON-Schema-validate a structured JSON export."""
    try:
        console.print(f"[green]JSON export:[/green] {export_json()}")
    except (OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc


@export_app.command("csv")
def export_csv_command():
    """Export normalized observations to CSV."""
    console.print(f"[green]CSV export:[/green] {export_csv()}")


@workspace_app.command("status")
def workspace_status_command():
    current = workspace_status()
    _table("FBSU workspace", tuple(current.keys()), [current])


if __name__ == "__main__":
    app()
