import json
from typing import Any, Dict, List
from pathlib import Path

def pretty_json(data: Any) -> str:
    """Convert data to pretty JSON string."""
    return json.dumps(data, indent=2, ensure_ascii=False)

def compact_json(data: Any) -> str:
    """Convert data to compact JSON string."""
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

def validate_json_string(json_str: str) -> bool:
    """Validate if string is valid JSON."""
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

def merge_json_objects(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two JSON objects."""
    result = base.copy()

    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json_objects(result[key], value)
        else:
            result[key] = value

    return result

def extract_keys_from_json(data: Any, prefix: str = "") -> List[str]:
    """Extract all keys from nested JSON structure."""
    keys = []

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            keys.extend(extract_keys_from_json(value, full_key))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            full_key = f"{prefix}[{i}]"
            keys.extend(extract_keys_from_json(item, full_key))

    return keys

def filter_json_by_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter JSON object to only include specified keys."""
    result = {}

    for key in keys:
        if '.' in key:
            parts = key.split('.')
            current = data
            for part in parts[:-1]:
                if part in current:
                    current = current[part]
                else:
                    break
            else:
                if parts[-1] in current:
                    result[key] = current[parts[-1]]
        else:
            if key in data:
                result[key] = data[key]

    return result