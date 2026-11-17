import csv, json
from pathlib import Path

ALLOWED_TYPES = {"assets", "endpoints", "findings"}

def load_json(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise ValueError("Expected a JSON object or array of objects.")
    return data

def load_csv(path: str) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))
