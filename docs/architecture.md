# Architecture

The CLI is the entry point. Domain services validate and construct Pydantic
records, then persist them through the SQLite repository. Reports and exports
read from the repository and write into the engagement workspace.

```text
CLI
 ├── Core (config, workspace, database, scope guard)
 ├── Inventory (assets, endpoints)
 ├── Assessment (findings, evidence)
 ├── Importers (local files only)
 └── Reporting (Markdown, JSON)
```

The integration package contains an adapter contract only. It intentionally does
not launch scanners or perform network operations.
