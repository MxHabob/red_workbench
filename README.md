# Target Intelligence Workspace

This repository is a reusable workspace for organizing information about multiple
current and future targets. Each target has its own folder for its definition,
sources, local files, normalized data, and reports. FBSU is the initial example,
not the only supported target.

The workspace is for organizing target information and operator-provided files.
It is not a scanner, dashboard, or autonomous collection service.

## Safety boundary

- Every domain in a target's `target.yaml` is a candidate until ownership and
  authorization are independently confirmed.
- The scripts make no DNS, HTTP, TLS, or Censys API requests.
- Third-party systems and discovered IP addresses are not automatically in scope.
  Imported IP observations are marked `requires_authorization`.
- Do not retain credentials, cookies, tokens, private records, or target response
  bodies in this workspace.
- Any testing beyond local file organization requires written authorization.

## Per-target structure

Each target has a separate directory under `targets/`:

```text
targets/
  <target-name>/
    target.yaml          identity, domains, and scope policy
    sources.yaml         source references and public metadata URLs
    files/
      imports/           optional operator-held original files
      evidence/          locally retained evidence, if authorized
    data/                normalized local datasets
    reports/             target-specific reports
```

The committed starter target is [FBSU](./targets/fbsu/target.yaml), with its
sources in [sources.yaml](./targets/fbsu/sources.yaml). Its domains and references
were supplied as candidates; their ownership, availability, and contents have
not been checked.

To add another target, create a sibling folder such as `targets/example/` with
its own `target.yaml` and `sources.yaml`. Keep its imports, data, evidence, and
reports inside that target's folder. The scripts accept a target file or folder
name; they do not have FBSU-specific discovery logic.

## Reusable scripts

Python 3.11+ is required. PyYAML is the only runtime dependency; pytest and Ruff
are development tools. No API credentials are required.

For a fresh environment:

```powershell
python -m pip install -e ".[dev]"
```

Validate a target file. This checks syntax and duplicates only; it performs no
DNS lookups and does not verify ownership:

```powershell
python scripts\validate_targets.py --file targets\fbsu\target.yaml
```

Normalize a manually exported Censys file for the selected target:

```powershell
python scripts\normalize_censys_export.py `
  --target fbsu `
  --input .\targets\fbsu\files\imports\censys-export.json `
  --source-reference "https://platform.censys.io/search?q=fbsu.edu.sa"
```

The normalizer accepts local JSON or CSV, keeps a limited set of non-sensitive
scalar fields, and enforces 10 MiB and 10,000-row limits. It writes normalized
observations to `targets\<target>\data\censys-normalized.json` by default, with
timestamps, source reference, confidence, verification status, and a SHA-256
reference to the input. It does not preserve or copy the raw export, use Censys
credentials, or authorize imported IP addresses. Use the actual source reference
for each target.

Operational `data/`, `files/`, and `reports/` contents are ignored by Git; the
`.gitkeep` files preserve the agreed empty folders. See [.gitignore](./.gitignore).

## Project files

```text
targets/                  one information folder per target
scripts/                  reusable local-file utilities
tests/                    tests for the utilities
pyproject.toml             dependencies and development-tool settings
```

Run the tests and focused lint checks with:

```powershell
python -m pytest
ruff check scripts\validate_targets.py scripts\normalize_censys_export.py tests\test_inventory_scripts.py
```
