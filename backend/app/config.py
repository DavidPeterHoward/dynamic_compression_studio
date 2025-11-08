"""
Configuration management for the Dynamic Compression Algorithms backend.
"""

from typing import Optional, List, Union
from pydantic import Field, validator, field_validator
from pydantic_settings import BaseSettings
import os
import json


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: Optional[str] = Field(default=None, env="DATABASE_URL")
    host: str = Field(default="localhost", env="POSTGRES_SERVER")
    port: int = Field(default=5432, env="POSTGRES_PORT")
    username: str = Field(default="compression_user", env="POSTGRES_USER")
    password: str = Field(default="compression_password", env="POSTGRES_PASSWORD")
    database: str = Field(default="compression_db", env="POSTGRES_DB")
    use_sqlite: bool = Field(default=True, env="USE_SQLITE")  # Default to SQLite for development
    
    @property
    def sync_url(self) -> str:
        """Get database URL for SQLAlchemy."""
        # Check environment variable first
        import os
        env_url = os.environ.get("DATABASE_URL")
        if env_url:
            return env_url
        
        # Use SQLite for development if configured
        if self.use_sqlite:
            return "sqlite:///./compression_dev.db"
        
        if self.url:
            return self.url
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_url(self) -> str:
        """Get async database URL for SQLAlchemy."""
        # Check environment variable first
        import os
        env_url = os.environ.get("DATABASE_URL")
        if env_url:
            # Convert sync URL to async URL
            if env_url.startswith("postgresql://"):
                return env_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif env_url.startswith("sqlite://"):
                return env_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
            return env_url
        
        # Use SQLite for development if configured
        if self.use_sqlite:
            return "sqlite+aiosqlite:///./compression_dev.db"
        
        if self.url:
            # Convert sync URL to async URL
            if self.url.startswith("postgresql://"):
                return self.url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif self.url.startswith("sqlite://"):
                return self.url.replace("sqlite://", "sqlite+aiosqlite://", 1)
            return self.url
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    database: int = Field(default=0, env="REDIS_DB")


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)


class CompressionSettings(BaseSettings):
    """Compression algorithm configuration settings."""
    
    max_file_size: int = Field(default=100 * 1024 * 1024)  # 100MB
    supported_formats: List[str] = Field(default=[
        "txt", "json", "xml", "csv", "py", "js", "ts", "html", "css", "md",
        "log", "sql", "yaml", "yml", "toml", "ini", "cfg", "conf"
    ])
    compression_levels: List[int] = Field(default=[1, 3, 6, 9])
    chunk_size: int = Field(default=8192)
    max_workers: int = Field(default=4)


class APISettings(BaseSettings):
    """API configuration settings."""

    model_config = {"extra": "ignore"}

    title: str = Field(default="Dynamic Compression Algorithms API")
    description: str = Field(default="Advanced compression optimization with AI")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=True, env="DEBUG")  # Enable debug mode by default for documentation
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    cors_methods: str = Field(default="*", env="CORS_METHODS")
    cors_headers: str = Field(default="*", env="CORS_HEADERS")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [item.strip() for item in self.cors_origins.split(',') if item.strip()]
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Get CORS methods as a list."""
        if self.cors_methods == "*":
            return ["*"]
        return [item.strip() for item in self.cors_methods.split(',') if item.strip()]
    
    @property
    def cors_headers_list(self) -> List[str]:
        """Get CORS headers as a list."""
        if self.cors_headers == "*":
            return ["*"]
        return [item.strip() for item in self.cors_headers.split(',') if item.strip()]


class Settings(BaseSettings):
    """Main application settings."""
    
    # Core settings
    app_name: str = Field(default="Dynamic Compression Algorithms")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    compression: CompressionSettings = CompressionSettings()
    api: APISettings = APISettings()
    
    # File storage
    upload_dir: str = Field(default="./uploads")
    temp_dir: str = Field(default="./temp")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json")
    
    # Performance
    max_concurrent_requests: int = Field(default=100)
    request_timeout: int = Field(default=300)
    
    # Additional fields from env.example to prevent validation errors
    version: Optional[str] = Field(default="1.0.0", env="VERSION")
    debug: Optional[bool] = Field(default=True, env="DEBUG")
    secret_key: Optional[str] = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: Optional[str] = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: Optional[int] = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: Optional[int] = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    postgres_server: Optional[str] = Field(default="localhost", env="POSTGRES_SERVER")
    postgres_user: Optional[str] = Field(default="compression_user", env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default="compression_password", env="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(default="compression_db", env="POSTGRES_DB")
    postgres_db_test: Optional[str] = Field(default="compression_db_test", env="POSTGRES_DB_TEST")
    postgres_port: Optional[int] = Field(default=5432, env="POSTGRES_PORT")
    redis_host: Optional[str] = Field(default="localhost", env="REDIS_HOST")
    redis_port: Optional[int] = Field(default=6379, env="REDIS_PORT")
    redis_db: Optional[int] = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    max_file_size: Optional[int] = Field(default=104857600, env="MAX_FILE_SIZE")
    smtp_tls: Optional[bool] = Field(default=True, env="SMTP_TLS")
    smtp_port: Optional[int] = Field(default=587, env="SMTP_PORT")
    smtp_host: Optional[str] = Field(default="smtp.localhost", env="SMTP_HOST")
    smtp_user: Optional[str] = Field(default="your-email@localhost", env="SMTP_USER")
    smtp_password: Optional[str] = Field(default="your-app-password", env="SMTP_PASSWORD")
    emails_from_email: Optional[str] = Field(default="your-email@localhost", env="EMAILS_FROM_EMAIL")
    emails_from_name: Optional[str] = Field(default="File Service Team", env="EMAILS_FROM_NAME")
    email_reset_token_expire_hours: Optional[int] = Field(default=24, env="EMAIL_RESET_TOKEN_EXPIRE_HOURS")
    backend_cors_origins: Optional[List[str]] = Field(default=["http://localhost:3000"], env="BACKEND_CORS_ORIGINS")
    
    @field_validator('backend_cors_origins', mode='before')
    @classmethod
    def parse_backend_cors_origins(cls, v):
        if isinstance(v, str):
            # Try JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated values
                return [item.strip() for item in v.split(',') if item.strip()]
        return v
    first_superuser: Optional[str] = Field(default="admin@localhost", env="FIRST_SUPERUSER")
    first_superuser_password: Optional[str] = Field(default="admin123", env="FIRST_SUPERUSER_PASSWORD")
    health_check_interval: Optional[int] = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    rate_limit_per_minute: Optional[int] = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    compression_quality: Optional[int] = Field(default=85, env="COMPRESSION_QUALITY")
    compression_threads: Optional[int] = Field(default=4, env="COMPRESSION_THREADS")
    next_public_api_url: Optional[str] = Field(default="http://localhost:3300", env="NEXT_PUBLIC_API_URL")
    next_public_graphql_url: Optional[str] = Field(default="http://localhost:3300/graphql", env="NEXT_PUBLIC_GRAPHQL_URL")
    
    @validator("upload_dir", "temp_dir")
    def create_directories(cls, v):
        """Create directories if they don't exist."""
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields instead of raising validation errors


# Global settings instance
settings = Settings()






