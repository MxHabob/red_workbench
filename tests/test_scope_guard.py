import pytest
from redteam.core.workspace import create_engagement, engagement_path
from redteam.core.scope_guard import validate_url, ScopeError
import yaml

def test_scope_guard_accepts_subdomain(tmp_path, monkeypatch):
    monkeypatch.setenv("RTW_HOME", str(tmp_path))
    create_engagement("sample")
    p = engagement_path("sample") / "scope" / "scope.yaml"
    data = yaml.safe_load(p.read_text())
    data["scope"]["domains"] = ["example.test"]
    p.write_text(yaml.safe_dump(data))
    assert validate_url("sample", "https://api.example.test/health") == "api.example.test"

def test_scope_guard_rejects_unlisted_host(tmp_path, monkeypatch):
    monkeypatch.setenv("RTW_HOME", str(tmp_path))
    create_engagement("sample")
    with pytest.raises(ScopeError):
        validate_url("sample", "https://not-in-scope.test/")
