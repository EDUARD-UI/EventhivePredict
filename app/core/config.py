from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_token: str | None = None
    docs_enabled: bool = True
    score_high_threshold: int = 60
    score_medium_threshold: int = 30
    max_candidates: int = 200
    max_body_bytes: int = 65536

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
