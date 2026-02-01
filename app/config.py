import os

class Settings:
    APP_NAME = "LLM Chaos Engineering Platform"
    ENV = os.getenv("ENV", "dev")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "llama3")
    SECONDARY_MODEL = os.getenv("SECONDARY_MODEL", "mistral")

    ENABLE_CHAOS = os.getenv("ENABLE_CHAOS", "false").lower() == "true"

settings = Settings()
