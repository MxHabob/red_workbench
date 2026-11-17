# FBSU Target Workspace

This repository contains the supplied FBSU candidate inventory and a small set of
reusable scripts for validating target lists and normalizing operator-provided
Censys exports. It is a working folder for organizing target information, not a
scanner, dashboard, or autonomous collection service.

## Safety boundary

- Every FBSU domain in [targets/fbsu.yaml](./targets/fbsu.yaml) is a candidate.
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

`targets/fbsu.yaml` stores the supplied primary domain, candidate subdomains,
Censys search reference, and public metadata URLs. Availability and content have
not been checked. Add other organizations as separate target YAML files using
the same shape; the scripts are not tied to FBSU.

## Reusable scripts

Python 3.11+ and PyYAML are required. The existing project dependency includes
PyYAML; no new runtime packages or API credentials are needed.

```powershell
python scripts\validate_targets.py --file targets\fbsu.yaml
python scripts\normalize_censys_export.py --input .\censys-export.json --output .\workspace\fbsu\censys-normalized.json
```

`validate_targets.py` checks domain syntax and duplicates only; it performs no
DNS lookups and does not verify ownership.

`normalize_censys_export.py` accepts a local JSON or CSV export, keeps a small
allow-list of non-sensitive scalar fields, limits the file to 10 MiB/10,000 rows,
and writes normalized observations with source, timestamp, confidence, status,
and a SHA-256 reference to the imported file. It does not preserve the raw export
or use Censys credentials. Review ownership and authorization before acting on
any imported IP or third-party relationship.

## Layout

```text
targets/
  fbsu.yaml                 supplied FBSU candidate assets and public references
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
