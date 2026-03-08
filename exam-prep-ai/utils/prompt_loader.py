from pathlib import Path
from typing import Dict, Optional
from config.settings import PROJECT_ROOT

class PromptLoader:
    def __init__(self, prompts_dir: Optional[Path] = None):
        self.prompts_dir = prompts_dir or PROJECT_ROOT / 'prompts'
        self._cache: Dict[str, str] = {}

    def load_prompt(self, category: str, name: str) -> str:
        """Load prompt template from file."""
        cache_key = f"{category}/{name}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        prompt_path = self.prompts_dir / category / f"{name}.txt"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        self._cache[cache_key] = content
        return content

    def format_prompt(self, category: str, name: str, **kwargs) -> str:
        """Load and format prompt with variables."""
        template = self.load_prompt(category, name)
        return template.format(**kwargs)

    def get_available_prompts(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """Get list of available prompts."""
        if category:
            category_dir = self.prompts_dir / category
            if category_dir.exists():
                txt_files = [f.stem for f in category_dir.glob('*.txt')]
                return {category: txt_files}
            else:
                return {category: []}
        else:
            result = {}
            for category_dir in self.prompts_dir.iterdir():
                if category_dir.is_dir():
                    txt_files = [f.stem for f in category_dir.glob('*.txt')]
                    result[category_dir.name] = txt_files
            return result

# Global instance
prompt_loader = PromptLoader()