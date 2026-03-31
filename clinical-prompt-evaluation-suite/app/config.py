from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinical Prompt Evaluation Suite"
    environment: str = "development"
    database_url: str = "sqlite:///./clinical_prompt_eval.db"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_provider: str = "mock"
    mlflow_tracking_uri: str = "./mlruns"
    export_dir: str = "./artifacts/exports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
