"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Job Automation Bot"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    app_env: str = "development"
    secret_key: str = "your-secret-key-change-in-production"

    # Server
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000

    # Database
    database_url: str = "postgresql+psycopg://user:password@localhost:5432/job_bot_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM / Claude API
    anthropic_api_key: str = ""

    # Web Scraping
    proxy_url: Optional[str] = None
    captcha_api_key: Optional[str] = None

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Streamlit
    streamlit_server_port: int = 8501
    streamlit_theme_primary_color: str = "#0d47a1"

    # Job Scraping Configuration
    linkedin_search_query: str = "python developer"
    linkedin_search_location: str = "remote"
    indeed_search_query: str = "backend engineer"
    remoteok_tags: str = "python,remote"

    # User Profile
    user_full_name: str = ""
    user_email: str = ""
    user_phone: Optional[str] = None
    user_linkedin_url: Optional[str] = None
    user_github_url: Optional[str] = None
    user_location: str = "Remote"
    user_experience_years: int = 0

    # User Preferences
    salary_floor: Optional[int] = None
    remote_only: bool = True
    blacklist_companies: str = ""

    # Gmail API
    gmail_credentials_file: str = "credentials.json"
    gmail_token_file: str = "token.pickle"

    # Application Automation
    auto_apply_threshold: float = 0.75
    auto_apply_enabled: bool = False
    max_applications_per_day: int = 15
    min_seconds_between_submissions: int = 480  # 8 minutes

    # Slack Notifications
    slack_webhook_url: Optional[str] = None
    slack_notifications_enabled: bool = False

    # S3 / MinIO
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket_name: str = "job-bot-resumes"
    s3_region: str = "us-east-1"

    # Feature Flags
    enable_linkedin_scraper: bool = True
    enable_indeed_scraper: bool = True
    enable_remoteok_scraper: bool = True
    enable_llm_ranking: bool = True
    enable_gmail_monitoring: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

    @property
    def blacklist_companies_list(self) -> list[str]:
        """Parse blacklist_companies string to list"""
        if not self.blacklist_companies:
            return []
        return [c.strip() for c in self.blacklist_companies.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Default instance
settings = get_settings()
