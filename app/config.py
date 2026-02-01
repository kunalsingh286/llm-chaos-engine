import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "LLM Chaos Engineering Platform"
    ENV = os.getenv("ENV", "dev")

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "llama3")
    SECONDARY_MODEL = os.getenv("SECONDARY_MODEL", "mistral")

    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    CHROMA_PATH = "./chroma_db"

    ENABLE_CHAOS = os.getenv("ENABLE_CHAOS", "false").lower() == "true"


settings = Settings()
