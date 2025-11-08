"""Application Configuration Management"""
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from typing import Optional, List, Union
import logging


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Required fields will raise validation errors if not provided in production.
    """

    # Application Metadata
    APP_NAME: str = "AutoWeb Outreach AI API"
    API_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, production, test")
    DEBUG: bool = Field(default=True, description="Enable debug mode with verbose logging")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/autoweb_db",
        description="PostgreSQL database connection string"
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string for Celery message broker"
    )
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis host for rate limiting"
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis port for rate limiting"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis database number"
    )

    # Security Configuration
    JWT_SECRET: str = Field(
        default="CHANGE_THIS_IN_PRODUCTION",
        description="Secret key for JWT token signing - MUST be changed in production"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="Algorithm for JWT token encoding")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="JWT token expiration time in minutes (default: 24 hours)")

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT-4 template generation"
    )

    # Google API Configuration
    GOOGLE_API_KEY: Optional[str] = Field(
        default=None,
        description="Google API key for PageSpeed Insights / Lighthouse API"
    )

    # Premium Template Generation Configuration
    UNSPLASH_API_KEY: Optional[str] = Field(
        default=None,
        description="Unsplash API Access Key for premium business images (FREE tier: 50 requests/hour)"
    )
    PEXELS_API_KEY: Optional[str] = Field(
        default=None,
        description="Pexels API Key for hero background videos (FREE tier: 200 requests/hour)"
    )
    PREMIUM_TEMPLATE_MODE: bool = Field(
        default=True,
        description="Enable premium template generation with glassmorphism, animations, and rich media"
    )
    DEFAULT_IMAGE_COUNT: int = Field(
        default=15,
        description="Number of images to fetch per business template (12-20 recommended)"
    )
    ENABLE_VIDEO_BACKGROUNDS: bool = Field(
        default=True,
        description="Enable hero background video fetching from Pexels"
    )

    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default=[f"http://localhost:{port}" for port in range(3000, 3010)],  # Allow localhost ports 3000-3009
        description="Allowed CORS origins for frontend applications (comma-separated string or list)"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS requests")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], description="Allowed HTTP methods for CORS")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], description="Allowed HTTP headers for CORS")

    @validator("JWT_SECRET")
    def validate_jwt_secret_in_production(cls, v, values):
        """Ensure JWT_SECRET is changed in production environment"""
        environment = values.get("ENVIRONMENT", "development")
        if environment == "production" and v == "CHANGE_THIS_IN_PRODUCTION":
            raise ValueError("JWT_SECRET must be changed in production environment")
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure DATABASE_URL is properly formatted"""
        if not v.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL connection string")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Ensure LOG_LEVEL is valid"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v.upper()

    @validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list, always return list"""
        if isinstance(v, str):
            # Support comma-separated string from environment variables
            if not v.strip():
                return ["http://localhost:3000", "http://localhost:3001"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        else:
            return ["http://localhost:3000", "http://localhost:3001"]

    def configure_logging(self) -> None:
        """Configure application logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Configure logging on module import
settings.configure_logging()

# Debug: Print API key on startup
import logging
logger = logging.getLogger(__name__)
logger.info(f"[CONFIG] GOOGLE_API_KEY loaded: {settings.GOOGLE_API_KEY[:30] if settings.GOOGLE_API_KEY else 'None'}...")

# Force reload timestamp: 2025-11-04 22:10
