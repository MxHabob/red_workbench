from fbsu_intelligence.core.config import load_config


def list_sources() -> list[dict[str, str]]:
    entries = load_config("sources.yaml").get("sources", [])
    return [
        {
            "name": item["name"],
            "type": item["type"],
            "reference": item["reference"],
            "access": item["access"],
            "reliability": item["reliability"],
        }
        for item in entries
    ]
