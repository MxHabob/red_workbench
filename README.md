# FBSU Target Workspace

This repository contains the supplied FBSU candidate inventory and a small set of
reusable scripts for validating target lists and normalizing operator-provided
Censys exports. It is a working folder for organizing target information, not a
scanner, dashboard, or autonomous collection service.

## Safety boundary

- Every FBSU domain in [targets/fbsu/target.yaml](./targets/fbsu/target.yaml) is a candidate.
  The list does not prove ownership or permission.
- The scripts make no DNS, HTTP, TLS, or Censys API requests.
- The IP-based `/.well-known/` reference is recorded but not accessed or
  authorized.
- Censys imports are local files only. IP observations are marked
  `requires_authorization` and are never added to scope.
- Do not add credentials, cookies, tokens, private records, or target response
  bodies to this workspace.
- Any testing beyond local file organization requires written authorization.

## Target record

Each target has its own folder. For FBSU, `targets/fbsu/target.yaml` contains
identity, candidate domains, and scope policy; `targets/fbsu/sources.yaml`
contains source and metadata references. Availability and content have not been
checked. Add another target as a sibling folder with the same two files; the
scripts accept any target definition.

## Reusable scripts

Python 3.11+ is required. PyYAML is the only runtime dependency; pytest and Ruff
are development tools. No API credentials are needed.

For a fresh environment, install the repository dependencies once:

```powershell
python -m pip install -e ".[dev]"
```

```powershell
python scripts\validate_targets.py --file targets\fbsu\target.yaml
python scripts\normalize_censys_export.py --target fbsu --input .\targets\fbsu\files\imports\censys-export.json --source-reference "https://platform.censys.io/search?q=fbsu.edu.sa"
```

`validate_targets.py` checks domain syntax and duplicates only; it performs no
DNS lookups and does not verify ownership.

`normalize_censys_export.py` accepts a local JSON or CSV export, keeps a small
allow-list of non-sensitive scalar fields, limits the file to 10 MiB/10,000 rows,
and writes normalized observations with source, timestamp, confidence, status,
and a SHA-256 reference to the imported file. It does not preserve the raw export
or use Censys credentials. Review ownership and authorization before acting on
any imported IP or third-party relationship.
The normalized output defaults to `targets\<target>\data\censys-normalized.json`;
use `--output` only when you need a different location.
Put operator-held input exports under `targets\<target>\files\imports\` if you
choose to retain them; the normalizer reads them in place and does not copy them.
Generated data, retained files, and reports are ignored by Git. These folders
are created only when needed, so unused empty folders are not added.

## Layout

```text
targets/
  fbsu/
    target.yaml             candidate assets and scope policy
    sources.yaml            public-source references
    files/
      imports/               optional operator-held original files
      evidence/              locally retained evidence, if authorized
    data/                    normalized local datasets (generated)
    reports/                 target-specific reports (generated)
scripts/
  validate_targets.py       syntax and duplicate checks for any target file
  normalize_censys_export.py local, bounded JSON/CSV normalization
tests/
  test_inventory_scripts.py
```

Run the focused checks with:

```powershell
python -m pytest
ruff check scripts\validate_targets.py scripts\normalize_censys_export.py tests\test_inventory_scripts.py
```
