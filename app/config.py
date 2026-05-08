from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Restaurant Recommendation API")
    debug: bool = Field(default=False)

    hf_home: Optional[str] = Field(
        default=None,
        description="Optional override for Hugging Face cache root (HF_HOME).",
    )
    hf_datasets_cache: Optional[str] = Field(
        default=None,
        description="Optional override for datasets library cache path.",
    )

    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI-compatible API base URL.",
    )
    llm_api_key: Optional[str] = Field(default=None)
    llm_model: str = Field(default="gpt-4o-mini")

    llm_enabled: bool = Field(
        default=True,
        description="When false, recommendation flow may skip the LLM (later phases).",
    )
    llm_timeout_seconds: float = Field(default=60.0, ge=1.0)
    llm_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Default number of ranked recommendations to request from the LLM.",
    )

    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        description="Groq OpenAI-compatible API base URL.",
    )
    groq_api_key: Optional[str] = Field(
        default=None,
        description="Groq API key used in Phase 4 recommendation engine.",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq chat model for restaurant ranking and explanations.",
    )

    zomato_dataset_id: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        description="Hugging Face dataset id when not using a local CSV.",
    )
    zomato_csv_path: Optional[str] = Field(
        default=None,
        description="If set, load this CSV instead of the Hugging Face hub (tests / offline).",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
