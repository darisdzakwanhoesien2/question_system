import os
import json
from pathlib import Path
from typing import Dict, Any, List

def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if not."""
    path.mkdir(parents=True, exist_ok=True)

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON file and return dictionary."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save dictionary to JSON file."""
    ensure_directory(file_path.parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def list_files_in_directory(directory: Path, extension: str = None) -> List[Path]:
    """List all files in directory, optionally filter by extension."""
    if not directory.exists():
        return []

    files = []
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            if extension is None or file_path.suffix == extension:
                files.append(file_path)

    return files

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB."""
    return file_path.stat().st_size / (1024 * 1024)

def safe_filename(filename: str) -> str:
    """Create safe filename by removing/replacing invalid characters."""
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', filename)