from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

WEBAPP_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=WEBAPP_ROOT / ".env", extra="ignore")

    artifacts_dir: Path = WEBAPP_ROOT / "artifacts"
    data_csv: Path = WEBAPP_ROOT / "data" / "Diseases_and_Symptoms_dataset.csv"
    database_path: Path = WEBAPP_ROOT / "data" / "app.db"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_provider: str = "none"


settings = Settings()
