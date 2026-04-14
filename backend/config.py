from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/finhub"
    redis_url: str = "redis://localhost:6379/0"

    # Free APIs
    fred_api_key: str = ""
    alpha_vantage_key: str = ""
    twelve_data_key: str = ""
    polygon_key: str = ""
    tiingo_key: str = ""
    finnhub_api_key: str = ""
    marketaux_key: str = ""
    news_api_key: str = ""
    openfigi_key: str = ""

    # Broker APIs
    upstox_api_key: str = ""
    upstox_api_secret: str = ""
    upstox_redirect_uri: str = "http://localhost:8080"
    upstox_access_token: str = ""
    nse_cookies: str = ""

    # Ollama AI
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_embed_model: str = "nomic-embed-text"

    # Alerts
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Features
    sentiment_finbert_enabled: bool = False
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # India tax defaults (FY 2024-25)
    india_stcg_equity_rate: float = 0.20
    india_ltcg_equity_rate: float = 0.125
    india_ltcg_equity_exemption_inr: float = 125_000.0
    india_ltcg_holding_days: int = 365
    india_fo_audit_turnover_inr: float = 100_000_000.0
    india_stt_option_sell_on_exercise_pct: float = 0.00125


@lru_cache
def get_settings() -> Settings:
    return Settings()
