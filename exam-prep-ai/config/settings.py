import os
import yaml
from pathlib import Path
from typing import Dict, Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def load_settings() -> Dict[str, Any]:
    """Load all application settings."""
    settings = {
        'project_root': PROJECT_ROOT,
        'storage_dir': PROJECT_ROOT / 'storage',
        'datasets_dir': PROJECT_ROOT / 'datasets',
        'prompts_dir': PROJECT_ROOT / 'prompts',
        'config_dir': PROJECT_ROOT / 'config',
    }

    # Load LLM config
    llm_config_path = PROJECT_ROOT / 'config' / 'llm_config.yaml'
    if llm_config_path.exists():
        settings['llm'] = load_yaml_config(str(llm_config_path))
    else:
        settings['llm'] = {}

    # Load exam config
    exam_config_path = PROJECT_ROOT / 'config' / 'exam_config.yaml'
    if exam_config_path.exists():
        settings['exam'] = load_yaml_config(str(exam_config_path))
    else:
        settings['exam'] = {}

    return settings

# Global settings instance
SETTINGS = load_settings()