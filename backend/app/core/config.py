from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sahayak API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "sahayak"

    openai_api_key: str = ""
    openai_whisper_model: str = "whisper-1"
    openai_action_model: str = "gpt-4o-mini"

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:5173"

    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    upload_dir: str = "uploads"
    max_file_size_mb: int = 50
    mongodb_connect_retries: int = 5
    mongodb_retry_delay_seconds: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
