"""
NUX Agent — Centralized Settings
Loads configuration from .env file in project root.
"""

import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class Settings:
    """Centralized configuration for NUX Agent."""

    # LLM Provider
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    LLM_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
    LLM_API_KEY: str = os.getenv("API_KEY", "")
    LLM_MODEL: str = os.getenv("MODEL", "llama-3.3-70b-versatile")

    # API Keys
    BASESCAN_API_KEY: str = os.getenv("BASESCAN_API_KEY", "")
    GOPLUS_API_KEY: str = os.getenv("GOPLUS_API_KEY", "")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Interface
    INTERFACE: str = os.getenv("INTERFACE", "cli")

    # Agent Identity
    AGENT_NAME: str = "NUX"
    AGENT_VERSION: str = "2.1.0"
    DEFAULT_CHAIN: str = "base"
    DEFAULT_CHAIN_ID: str = "8453"

    # Persona
    @staticmethod
    def load_persona() -> str:
        persona_path = os.path.join(os.path.dirname(__file__), "persona.txt")
        if os.path.exists(persona_path):
            with open(persona_path, "r") as f:
                return f.read().strip()
        return "You are NUX, a toxic onchain AI agent on Base."


settings = Settings()
