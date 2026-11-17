import json

from scripts.normalize_censys_export import normalize_records
from scripts.validate_targets import validate_target_data


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
