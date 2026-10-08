"""Application configuration, loaded from environment variables (prefix ``LS_``)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LS_", env_file=".env", extra="ignore")

    environment: str = "local"

    # Classifier probability at/above which an input is blocked, and at/above
    # which it is flagged for review.
    block_threshold: float = 0.8
    flag_threshold: float = 0.5

    # A secret token embedded in the application's system prompt. If it ever
    # appears in model output, the system prompt has leaked.
    system_prompt_canary: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
