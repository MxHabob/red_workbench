# Architecture

FBSU Intelligence is an additive local-only package alongside the existing
`redteam` workbench. Its CLI validates operator input, Pydantic models enforce
record shape, and a small SQLite repository persists normalized domain,
observation, metadata-reference, and collection-event records. No collector
module opens a network connection.

```text
fbsu-intel CLI
 ├── core/          validated models, YAML configuration, workspace, SQLite repository
 ├── intelligence/ source registry
 ├── integrations/  bounded Censys JSON/CSV import, allow-listed fields only
 └── reporting/     Markdown, HTML, JSON-Schema-validated JSON, CSV
```

Configuration under `config/` seeds the candidate inventory and static metadata
references. Workspace initialization copies this configuration and persists
domains as `candidate`. Imports are observations with source references and
timestamps; Censys IP records carry `requires_authorization`. A discovered address
is never converted into scope. JSON export validation uses
`schemas/fbsu-export.schema.json`.

The CLI's `targets verify` is strictly a syntax/duplicate check; it does not
perform DNS or ownership verification. Metadata results are manually entered
against pre-registered references. The integration intentionally has no Censys
API client: offline exports are the supported boundary.
