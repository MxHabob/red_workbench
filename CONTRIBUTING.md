# Contributing

These practices apply to all contributors, regardless of team size.

## Changes and branches

- Do not commit directly to `main`; create a short-lived branch for each task.
- Use a descriptive prefix, for example `feat/add-target-schema`,
  `docs/update-workflow`, or `fix/csv-import`.
- Keep a branch focused on one change. Avoid having multiple people edit the same
  target files concurrently; coordinate ownership or split targets/files.
- Sync with `main` before opening a pull request. Rebase your own unpublished
  branch when appropriate; do not rewrite another contributor's shared branch.
- Use clear commit subjects such as `feat(targets): add example target`.
- Never commit credentials, private records, raw imports, or generated target data.
  Keep operator-held material in the ignored `targets/<name>/files/` and
  `targets/<name>/data/` directories.

## Before opening a pull request

```powershell
python -m pytest
ruff check scripts\validate_targets.py scripts\normalize_censys_export.py tests\test_inventory_scripts.py
```

Describe the purpose, files changed, checks run, and any target-data handling in
the pull request. Add a reviewer who did not author the change when practical.

## Hosting settings

Configure these on the Git hosting service; they cannot be enforced by committed
repository files alone:

- Protect `main` and require pull requests for changes.
- Require at least one approval for non-trivial changes and dismiss stale
  approvals after new commits.
- Configure test/lint checks in the hosting service and require them to pass
  before merging.
- Block force-pushes and branch deletion on `main`.
- Prefer squash or rebase merges to keep the shared history easy to follow.

## Per-clone Git preferences

These settings are local to the current clone and are not shared by commits:

```powershell
git config --local pull.rebase true
git config --local fetch.prune true
git config --local push.autoSetupRemote true
```

Set `user.name` and `user.email` to your own identity on each machine; do not
copy another contributor's identity or add it to the repository.
