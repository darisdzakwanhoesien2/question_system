from typing import Dict, Any, Optional
from services.llm_service import llm_service

class LLMRouter:
    """Router for LLM requests based on task type and availability."""

    def __init__(self):
        self.task_mappings = {
            'essay_grading': 'essay_grader',
            'short_answer_grading': 'short_answer_grader',
            'performance_analysis': 'performance_analyzer',
            'learning_recommendations': 'learning_recommender'
        }

    def route_request(self, task: str, prompt: str, **kwargs) -> str:
        """
        Route LLM request to appropriate provider based on task.

        Args:
            task: Task type (essay_grading, short_answer_grading, etc.)
            prompt: The prompt to send
            **kwargs: Additional parameters for generation

        Returns:
            Generated response
        """
        # Try task-specific provider first
        if task in self.task_mappings:
            task_name = self.task_mappings[task]
            try:
                return llm_service.generate_for_task(task_name, prompt, **kwargs)
            except Exception as e:
                print(f"Task-specific provider failed for {task}: {e}")

        # Fallback to default provider
        return llm_service.generate(prompt, **kwargs)

    def get_provider_for_task(self, task: str) -> Optional[str]:
        """Get the provider name for a specific task."""
        if task in self.task_mappings:
            task_name = self.task_mappings[task]
            # Check if task has specific provider configured
            from config.settings import SETTINGS
            llm_config = SETTINGS.get('llm', {})
            tasks_config = llm_config.get('tasks', {})

            if task_name in tasks_config:
                return tasks_config[task_name].get('provider')

        return llm_service.default_provider

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available and working."""
        return llm_service.test_provider(provider_name)

    def get_fallback_chain(self, task: str) -> list:
        """Get fallback chain of providers for a task."""
        primary = self.get_provider_for_task(task)
        available = llm_service.get_available_providers()

        chain = []
        if primary and primary in available:
            chain.append(primary)

        # Add other available providers as fallback
        for provider in available:
            if provider not in chain:
                chain.append(provider)

        return chain

    def generate_with_fallback(self, task: str, prompt: str, **kwargs) -> str:
        """
        Generate with automatic fallback to other providers if primary fails.
        """
        fallback_chain = self.get_fallback_chain(task)

        for provider in fallback_chain:
            try:
                return llm_service.generate(prompt, provider=provider, **kwargs)
            except Exception as e:
                print(f"Provider {provider} failed: {e}")
                continue

        return "All providers failed. Please check your LLM configuration."

    def get_task_stats(self) -> Dict[str, Any]:
        """Get statistics about task routing."""
        stats = {
            'total_tasks': len(self.task_mappings),
            'configured_tasks': 0,
            'available_providers': len(llm_service.get_available_providers()),
            'task_provider_mapping': {}
        }

        from config.settings import SETTINGS
        llm_config = SETTINGS.get('llm', {})
        tasks_config = llm_config.get('tasks', {})

        for task, task_config in tasks_config.items():
            provider = task_config.get('provider')
            if provider and provider in llm_service.providers:
                stats['configured_tasks'] += 1
                stats['task_provider_mapping'][task] = provider

        return stats

# Global instance
llm_router = LLMRouter()