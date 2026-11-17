from urllib.parse import urlparse
import ipaddress
import yaml
from redteam.core.workspace import engagement_path

class ScopeError(ValueError):
    pass

def _host_matches(host: str, domain: str) -> bool:
    host, domain = host.lower().rstrip("."), domain.lower().lstrip("*.").rstrip(".")
    return host == domain or host.endswith("." + domain)

def validate_url(name: str, url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ScopeError("Only absolute HTTP(S) URLs with a hostname are accepted.")
    scope_file = engagement_path(name) / "scope" / "scope.yaml"
    if not scope_file.exists():
        raise ScopeError("Scope file is missing.")
    data = yaml.safe_load(scope_file.read_text(encoding="utf-8")) or {}
    scope = data.get("scope", {})
    host = parsed.hostname.lower()
    for excluded in scope.get("excluded_domains", []):
        if _host_matches(host, excluded):
            raise ScopeError(f"Host is explicitly excluded: {host}")
    for allowed in scope.get("domains", []):
        if _host_matches(host, allowed):
            return host
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        raise ScopeError(f"Host is not listed in the engagement scope: {host}")
    for excluded in scope.get("excluded_ip_ranges", []):
        if ip in ipaddress.ip_network(excluded, strict=False):
            raise ScopeError(f"IP is explicitly excluded: {host}")
    for allowed in scope.get("ip_ranges", []):
        if ip in ipaddress.ip_network(allowed, strict=False):
            return host
    raise ScopeError(f"Host is not listed in the engagement scope: {host}")
