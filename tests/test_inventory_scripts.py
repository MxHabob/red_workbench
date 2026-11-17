import json
from pathlib import Path

from scripts.normalize_censys_export import default_output_path, normalize_records
from scripts.validate_targets import validate_target_data


def test_fbsu_file_contains_only_supplied_candidate_inventory():
    import yaml

    data = yaml.safe_load(Path("targets/fbsu/target.yaml").read_text(encoding="utf-8"))
    sources = yaml.safe_load(Path("targets/fbsu/sources.yaml").read_text(encoding="utf-8"))

    assert data["status"] == "candidate"
    assert len(data["domains"]) == 10
    assert data["policy"]["network_collection"] == "disabled"
    assert len(sources["public_metadata_references"]) == 11


def test_target_files_have_separate_working_data_locations():
    assert default_output_path("fbsu") == Path("targets/fbsu/data/censys-normalized.json")
    try:
        default_output_path("../outside")
    except ValueError:
        pass
    else:
        raise AssertionError("Target name must not allow path traversal.")


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
