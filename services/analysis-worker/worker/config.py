from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    log_level: str = "INFO"
    database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    qdrant_url: str = "http://qdrant:6333"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "autotune-graph"
    anthropic_api_key: str | None = None
    anthropic_model_reasoning: str = "claude-opus-4-8"
    anthropic_model_analysis: str = "claude-sonnet-4-6"
    voyage_api_key: str | None = None
    embed_model: str = "voyage-3"
    s3_endpoint: str | None = None
    s3_bucket: str = "autotune-artifacts"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
