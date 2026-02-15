"""Configuration for Nexora Search Engine."""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis DB")
    cache_ttl: int = Field(default=3600, description="Cache TTL seconds")
    max_results: int = Field(default=10, ge=1, le=100)
    max_crawl_pages: int = Field(default=100, ge=1)
    crawl_timeout: int = Field(default=10, ge=1)
    max_page_size: int = Field(default=10000, ge=100)
    user_agent: str = Field(default="Nexora-Bot/1.0 (Educational Search Engine)")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: List[str] = Field(default=["*"])
    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
