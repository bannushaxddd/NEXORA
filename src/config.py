"""Configuration for Nexora Search Engine."""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Redis configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis DB")
    cache_ttl: int = Field(default=3600, description="Cache TTL seconds")
    use_cache: bool = Field(default=True, description="Enable or disable Redis caching")

    # Search engine configuration
    max_results: int = Field(default=10, ge=1, le=100)
    bm25_k1: float = Field(default=1.5, description="BM25 k1")
    bm25_b: float = Field(default=0.75, description="BM25 b")
    max_crawl_pages: int = Field(default=100, ge=1)
    crawl_timeout: int = Field(default=10, ge=1)
    max_page_size: int = Field(default=10000, ge=100)
    user_agent: str = Field(default="Nexora-Bot/1.0 (Educational Search Engine)")

    # API configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    log_level: str = Field(default="INFO", description="Logging level")

    # Pydantic settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_redis_url(self) -> Optional[str]:
        """Return Redis URL or None if caching is disabled."""
        if self.use_cache:
            return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return None


# Create a single settings instance
settings = Settings()
