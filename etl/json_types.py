import json
from pathlib import Path
from typing import Any

def read_json_records(path: Path) -> list[dict[str, Any]]:
    """Safely reads a JSON file and ensures it returns a list of dictionaries."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected JSON list, got {type(data).__name__}")
    return data

def require_keys(record: dict[str, Any], required: list[str], context: str = "") -> None:
    """Verifies that a record contains all required keys."""
    missing = [k for k in required if k not in record]
    if missing:
        raise KeyError(f"Missing required keys {missing} in {context}: {record!r}")
