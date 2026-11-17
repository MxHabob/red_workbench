# FBSU Intelligence

FBSU Intelligence is a Python 3.11+ local workspace for organizing public-source
asset-intelligence references and operator-provided observations. It uses Typer,
Pydantic, SQLite, PyYAML, Rich, JSON Schema, pytest, and Ruff. It does not scan or
contact FBSU systems.

## Safety and evidence boundaries

The default operating mode is **passive, offline, and manual-import-only**:

- The supplied FBSU domain names are candidates, not verified organizational assets.
- The tool makes no DNS, HTTP, TLS, Censys API, or other network requests.
- Censys integration accepts local JSON/CSV exports only. It does not read API
  credentials. The Censys search link is a reference, not proof of API access.
- Imported IP observations are marked `requires_authorization`; no IP is added to
  domain scope or automatically authorized.
- Third-party infrastructure and newly found subdomains require ownership and
  written authorization review.
- The application has no exploit, login, password-attack, bypass, crawl, or
  destructive-testing features.
- Only allow-listed scalar fields are retained from Censys files. Raw exports are
  not copied into the workspace. Do not import secrets, credentials, cookies,
  tokens, or private/personal records.

The manually supplied `http://15.204.235.208/.well-known/` reference is recorded
as a reference only; the IP is not treated as FBSU-owned and the application will
not access it.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Set `FBSU_INTEL_HOME` to choose another output directory. By default, workspace
data is stored in `.\workspace\fbsu`. No `.env` file or credentials are required.

## Quick start

```powershell
fbsu-intel init
fbsu-intel targets list
fbsu-intel targets verify
fbsu-intel sources
fbsu-intel metadata inventory
fbsu-intel workspace status
fbsu-intel report generate
fbsu-intel export json
fbsu-intel export csv
```

`targets verify` checks only syntax and duplicate names. It does not resolve,
contact, or verify domain ownership. Initialization creates the local database,
workspace folders, and ten candidate domains plus eleven supplied metadata
references, all labeled unverified/not checked.

## CLI reference

```text
fbsu-intel init
fbsu-intel targets list
fbsu-intel targets verify
fbsu-intel sources
fbsu-intel censys status
fbsu-intel censys import PATH.json
fbsu-intel censys import PATH.csv
fbsu-intel metadata inventory
fbsu-intel metadata record URL --source-url EVIDENCE_REFERENCE [--status-code 200]
fbsu-intel assets list
fbsu-intel domains list
fbsu-intel technologies list
fbsu-intel dependencies list
fbsu-intel applications list
fbsu-intel observations add --category technology --asset NAME --source SOURCE --source-reference REF
fbsu-intel observations list [--category CATEGORY]
fbsu-intel report generate [--format markdown|html|all]
fbsu-intel export json
fbsu-intel export csv
fbsu-intel workspace status
```

`metadata record` stores manually supplied availability, HTTP status, content type,
response size, observation timestamp, and evidence/source URL for a URL already
in the supplied reference list. It never fetches the URL. `observations add`
requires a source name and source reference; `--status` and `--confidence` are
explicit operator-supplied assessments.

### Censys offline imports

Use an export created independently through an authorized workflow:

```powershell
fbsu-intel censys import .\censys-export.json
fbsu-intel observations list
```

The importer accepts `.json` and `.csv`, rejects files larger than 10 MiB and
imports above 10,000 rows, and stores selected scalar fields only (address,
hostname/domain, port, protocol, service, basic TLS/certificate metadata, ASN,
and location). API keys are not used. Verify source context and ownership before
relying on imported observations.

## Workspace and configuration

```text
config/
  settings.yaml             workspace settings and bounded import sizes
  targets.yaml              explicitly supplied candidate domains
  exclusions.yaml           third-party and exclusion policy
  sources.yaml              Censys reference and public metadata URLs
  collection-policy.yaml    passive-mode policy and prohibited actions
workspace/fbsu/
  engagement.yaml
  intelligence.sqlite3
  targets.yaml, sources.yaml, exclusions.yaml, collection-policy.yaml
  assets/ domains/ dns/ certificates/ technologies/ dependencies/
  public-metadata/ applications/ third-party/ evidence/ exports/ logs/ reports/
src/fbsu_intelligence/
  core/ integrations/ intelligence/ reporting/ cli.py
schemas/fbsu-export.schema.json
tests/
```

`FBSU_INTEL_HOME` sets the parent directory for `workspace/fbsu`. The local SQLite
repository has normalized tables for domains, observations, public metadata, and
collection events. Pydantic validates records; the JSON export is validated
against `schemas/fbsu-export.schema.json`. Workspace data is excluded from Git.
Back up and protect it according to your organization's data-handling rules.

Statuses are distinct: `discovered`, `candidate`, `observed`, `verified`,
`excluded`, and `requires_authorization`. This tool does not promote candidates
to verified automatically.

## Reports and exports

`report generate` creates Markdown and HTML under `workspace/fbsu/reports`.
`export json` writes a schema-validated normalized inventory; `export csv` writes
the observation ledger. Reports include source references, timestamps, confidence,
verification state, collection limitations, and explicit ownership/authorization
caveats. No target findings or scan results are fabricated.

## Development and tests

```powershell
python -m pytest
ruff check .
fbsu-intel --help
```

The previous `rtw` local assessment-workbench command and its package remain
available for existing users. FBSU Intelligence is additive and uses its own
`fbsu-intel` entry point and `FBSU_INTEL_HOME` setting.
