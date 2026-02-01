from app.config import settings
from app.models.ollama_client import OllamaClient


class FallbackRouter:
    def __init__(self):
        self.client = OllamaClient()
        self.primary = settings.PRIMARY_MODEL
        self.secondary = settings.SECONDARY_MODEL

    def generate(self, prompt: str) -> str:
        try:
            return self.client.generate(self.primary, prompt)
        except Exception:
            return self.client.generate(self.secondary, prompt)
