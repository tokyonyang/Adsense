from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    naver_client_id: str = ""
    naver_client_secret: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    wp_base_url: str = ""
    wp_username: str = ""
    wp_app_password: str = ""
    wp_default_status: str = "draft"

    default_user_id: str | None = None

    lookback_hours: int = 24
    fallback_lookback_hours: int = 48
    max_keywords: int = 30
    hot_issue_count: int = 10
    card_news_count: int = 3
    article_count: int = 3
    category_filter: str = "all"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
