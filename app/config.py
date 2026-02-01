import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Global configuration for LLM Chaos Engineering Platform
    """

    # --------------------------------
    # App
    # --------------------------------

    APP_NAME = "LLM Chaos Engineering Platform"
    ENV = os.getenv("ENV", "dev")

    DEBUG = ENV != "prod"

    # --------------------------------
    # Ollama / LLM
    # --------------------------------

    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    PRIMARY_MODEL = os.getenv(
        "PRIMARY_MODEL",
        "llama3"
    )

    SECONDARY_MODEL = os.getenv(
        "SECONDARY_MODEL",
        "mistral"
    )

    TERTIARY_MODEL = os.getenv(
        "TERTIARY_MODEL",
        "phi3"
    )

    DEFAULT_TEMPERATURE = float(
        os.getenv("DEFAULT_TEMPERATURE", "0.2")
    )

    MAX_TOKENS = int(
        os.getenv("MAX_TOKENS", "2048")
    )

    # --------------------------------
    # Embeddings / Retrieval
    # --------------------------------

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "all-MiniLM-L6-v2"
    )

    CHROMA_PATH = os.getenv(
        "CHROMA_PATH",
        "./chroma_db"
    )

    TOP_K = int(
        os.getenv("TOP_K", "3")
    )

    # --------------------------------
    # Chaos Engineering
    # --------------------------------

    ENABLE_CHAOS = (
        os.getenv("ENABLE_CHAOS", "true").lower() == "true"
    )

    CHAOS_CONFIG_PATH = os.getenv(
        "CHAOS_CONFIG_PATH",
        "policies/chaos_config.yaml"
    )

    # --------------------------------
    # Resilience / Recovery
    # --------------------------------

    MAX_RETRIES = int(
        os.getenv("MAX_RETRIES", "2")
    )

    CIRCUIT_FAILURE_THRESHOLD = int(
        os.getenv("CIRCUIT_FAILURE_THRESHOLD", "3")
    )

    CIRCUIT_RECOVERY_TIMEOUT = int(
        os.getenv("CIRCUIT_RECOVERY_TIMEOUT", "30")
    )

    CACHE_TTL = int(
        os.getenv("CACHE_TTL", "300")
    )

    CACHE_MAX_SIZE = int(
        os.getenv("CACHE_MAX_SIZE", "200")
    )

    # --------------------------------
    # Degradation / Safe Mode
    # --------------------------------

    DEGRADED_MODE = (
        os.getenv("DEGRADED_MODE", "false").lower() == "true"
    )

    SAFE_MODE_MAX_TOKENS = int(
        os.getenv("SAFE_MODE_MAX_TOKENS", "512")
    )

    SAFE_MODE_TEMPERATURE = float(
        os.getenv("SAFE_MODE_TEMPERATURE", "0.1")
    )

    # --------------------------------
    # Observability
    # --------------------------------

    ENABLE_METRICS = (
        os.getenv("ENABLE_METRICS", "true").lower() == "true"
    )

    ENABLE_TRACING = (
        os.getenv("ENABLE_TRACING", "false").lower() == "true"
    )

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )


# Singleton instance
settings = Settings()
