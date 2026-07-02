from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core
    app_env: Literal["local", "dev", "staging", "prod"] = "local"
    app_name: str = "autotune-ai"
    log_level: str = "INFO"
    secret_key: str = Field(min_length=32)

    # Data stores
    database_url: PostgresDsn
    timescale_url: PostgresDsn | None = None
    redis_url: RedisDsn

    # Brokers
    rabbitmq_url: str = "amqp://autotune:autotune@rabbitmq:5672//"
    celery_broker_url: str
    celery_result_backend: str

    # Vector + KG
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str | None = None
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "autotune-graph"

    # Object store
    s3_endpoint: str | None = None
    s3_bucket: str = "autotune-artifacts"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str = "us-east-1"

    # Anthropic
    anthropic_api_key: str | None = None
    anthropic_model_reasoning: str = "claude-opus-4-8"
    anthropic_model_analysis: str = "claude-sonnet-4-6"
    anthropic_model_routing: str = "claude-haiku-4-5-20251001"

    # Embeddings
    embed_provider: str = "voyage"
    voyage_api_key: str | None = None
    embed_model: str = "voyage-3"

    # Auth
    jwt_issuer: str = "https://auth.autotune.ai"
    jwt_audience: str = "autotune-api"
    jwt_access_ttl_seconds: int = 300
    jwt_refresh_ttl_seconds: int = 30 * 24 * 3600
    password_pepper: str = Field(default="dev-pepper-change-me", min_length=8)

    # OIDC
    oidc_discovery_url: str | None = None
    oidc_client_id: str | None = None
    oidc_client_secret: str | None = None

    # Billing
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    # Observability
    otel_exporter_otlp_endpoint: str | None = None
    sentry_dsn: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
