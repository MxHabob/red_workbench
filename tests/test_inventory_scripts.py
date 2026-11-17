import json
from pathlib import Path

from scripts.normalize_censys_export import normalize_records
from scripts.validate_targets import validate_target_data


def test_fbsu_file_contains_only_supplied_candidate_inventory():
    import yaml

    data = yaml.safe_load(Path("targets/fbsu.yaml").read_text(encoding="utf-8"))

    assert data["domain_status"] == "candidate"
    assert len(data["domains"]) == 10
    assert len(data["public_metadata_references"]) == 11
    assert data["policy"]["network_collection"] == "disabled"


def test_target_validation_checks_duplicates_without_network():
    assert validate_target_data(
        {"primary_domain": "example.test", "domains": ["example.test", "api.example.test"]}
    ) == []
    assert "'example.test': duplicate" in validate_target_data(
        {"primary_domain": "example.test", "domains": ["example.test", "example.test"]}
    )[0]


def test_censys_normalizer_filters_fields_and_never_authorizes_ips():
    result = normalize_records(
        [{"ip": "192.0.2.4", "port": 443, "api_token": "do-not-export", "service": "raw"}],
        "https://example.test/search",
        "digest",
    )

    assert result[0]["verification_status"] == "requires_authorization"
    assert result[0]["details"] == {"ip": "192.0.2.4", "port": 443}
    assert "do-not-export" not in json.dumps(result)
