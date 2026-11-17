import json

import pytest

from fbsu_intelligence.core.models import Domain, Observation, VerificationStatus
from fbsu_intelligence.core.workspace import (
    get_repository,
    initialize_workspace,
)
from fbsu_intelligence.integrations.censys_import import import_censys_file
from fbsu_intelligence.reporting.exporters import export_json
from fbsu_intelligence.reporting.report_generator import generate_markdown


def test_initialize_registers_only_unverified_supplied_candidates(tmp_path, monkeypatch):
    monkeypatch.setenv("FBSU_INTEL_HOME", str(tmp_path))
    path = initialize_workspace()

    domains = get_repository().list("domains")
    resources = get_repository().list("metadata_resources")

    assert len(domains) == 10
    assert {item["status"] for item in domains} == {"candidate"}
    assert len(resources) == 11
    assert (path / "engagement.yaml").is_file()


def test_domain_model_rejects_bad_names_and_normalizes():
    assert Domain(name="WWW.Example.test.").name == "www.example.test"
    with pytest.raises(ValueError):
        Domain(name="not a domain")


def test_censys_import_keeps_ip_out_of_authorized_scope_and_drops_secret_fields(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("FBSU_INTEL_HOME", str(tmp_path))
    initialize_workspace()
    export_file = tmp_path / "censys.json"
    export_file.write_text(
        json.dumps(
            [
                {
                    "ip": "192.0.2.10",
                    "port": 443,
                    "service": "https",
                    "api_token": "must-not-be-saved",
                }
            ]
        ),
        encoding="utf-8",
    )

    assert import_censys_file(export_file) == 1
    row = get_repository().list("observations")[0]
    assert row["verification_status"] == VerificationStatus.REQUIRES_AUTHORIZATION
    assert row["details"] == {"ip": "192.0.2.10", "port": 443, "service": "https"}
    assert "must-not-be-saved" not in json.dumps(row)
    assert get_repository().list("domains")[0]["status"] == "candidate"


def test_export_schema_and_report_keep_candidate_status_explicit(tmp_path, monkeypatch):
    monkeypatch.setenv("FBSU_INTEL_HOME", str(tmp_path))
    initialize_workspace()

    output = export_json()
    payload = json.loads(output.read_text(encoding="utf-8"))
    report = generate_markdown().read_text(encoding="utf-8")

    assert len(payload["domains"]) == 10
    assert "candidate" in report
    assert "Network collection performed by this workspace: **No**" in report


def test_observation_requires_source_and_timezone_aware_timestamps():
    with pytest.raises(ValueError):
        Observation(
            category="technology",
            asset="example.test",
            source="manual",
            source_reference="documentation",
            first_observed_at="2026-01-01T00:00:00",
        )
