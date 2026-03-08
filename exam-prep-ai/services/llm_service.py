from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import requests
import json
from config.settings import SETTINGS

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass

class OllamaProvider(LLMProvider):
    """Ollama LLM provider."""

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate text using Ollama."""
        url = f"{self.config['base_url']}/api/generate"

        payload = {
            "model": self.config['model'],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result.get('response', '')
        except Exception as e:
            print(f"Ollama generation failed: {e}")
            return ""

class LMStudioProvider(LLMProvider):
    """LM Studio provider."""

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate text using LM Studio."""
        url = f"{self.config['base_url']}/v1/chat/completions"

        payload = {
            "model": self.config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"LM Studio generation failed: {e}")
            return ""

class OpenRouterProvider(LLMProvider):
    """OpenRouter provider."""

    def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> str:
        """Generate text using OpenRouter."""
        url = f"{self.config['base_url']}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.config['model'],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"OpenRouter generation failed: {e}")
            return ""

class LLMService:
    """Main LLM service class."""

    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.task_providers = {}

        self._load_providers()

    def _load_providers(self):
        """Load configured providers."""
        llm_config = SETTINGS.get('llm', {})

        # Load general providers
        providers_config = llm_config.get('providers', {})
        for provider_name, config in providers_config.items():
            if provider_name == 'ollama':
                self.providers[provider_name] = OllamaProvider(config)
            elif provider_name == 'lmstudio':
                self.providers[provider_name] = LMStudioProvider(config)
            elif provider_name == 'openrouter':
                self.providers[provider_name] = OpenRouterProvider(config)

        # Set default provider
        self.default_provider = llm_config.get('default_provider', 'ollama')
        if self.default_provider not in self.providers:
            self.default_provider = next(iter(self.providers.keys())) if self.providers else None

        # Load task-specific providers
        tasks_config = llm_config.get('tasks', {})
        for task, task_config in tasks_config.items():
            provider_name = task_config['provider']
            if provider_name in self.providers:
                self.task_providers[task] = self.providers[provider_name]

    def generate(self, prompt: str, provider: Optional[str] = None, **kwargs) -> str:
        """Generate text using specified or default provider."""
        if not self.providers:
            return "No LLM providers configured"

        provider_name = provider or self.default_provider
        if provider_name not in self.providers:
            provider_name = next(iter(self.providers.keys()))

        provider_instance = self.providers[provider_name]
        return provider_instance.generate(prompt, **kwargs)

    def generate_for_task(self, task: str, prompt: str, **kwargs) -> str:
        """Generate text for specific task using configured provider."""
        if task in self.task_providers:
            provider = self.task_providers[task]
            return provider.generate(prompt, **kwargs)
        else:
            return self.generate(prompt, **kwargs)

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())

    def test_provider(self, provider_name: str) -> bool:
        """Test if provider is working."""
        if provider_name not in self.providers:
            return False

        try:
            response = self.providers[provider_name].generate("Hello", max_tokens=10)
            return bool(response.strip())
        except Exception:
            return False

# Global instance
llm_service = LLMService()