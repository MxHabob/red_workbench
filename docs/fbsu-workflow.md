# FBSU workspace workflow

1. Review `config/targets.yaml`, `config/sources.yaml`, and
   `config/collection-policy.yaml`. The listed domains and URLs are supplied
   candidates, not verified findings.
2. Run `fbsu-intel init` to create the local workspace. The CLI initializes
   records as candidate or not checked and makes no network requests.
3. Use `fbsu-intel targets verify` for syntax and duplicate checks only.
4. Import only authorized, locally available Censys JSON/CSV exports. Imported
   data is low-confidence third-party observation; IPs require authorization.
5. Add manually reviewed technology, dependency, application, or API observations
   with `fbsu-intel observations add`, always including the source reference.
6. If response metadata was captured under an independently authorized process,
   record it with `fbsu-intel metadata record`. This command does not fetch URLs.
7. Review ownership, third-party relationships, evidence references, and
   authorization status before generating or sharing reports.
8. Run `fbsu-intel report generate` and `fbsu-intel export json` or `csv`.

The application does not execute target-provided files or scripts, retain raw
response bodies, or collect secrets or personal records. Reports describe only
provided references and imported/manual observations; they do not imply that
assets were reachable, scanned, or vulnerability-tested.
