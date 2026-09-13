from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    app_name: str = "VisioSync API"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"
    data_dir: Path = ROOT_DIR / "data"
    upload_dir: Path = ROOT_DIR / "uploads"
    database_url: str = "sqlite:///./data/visiosync.db"
    max_upload_mb: int = 100
    render_scale: float = 1.3
    max_retrieval_pages: int = 6
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = ""
    colpali_model: str = "vidore/colpali-v1.2"
    embedding_device: str = "auto"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    def prepare_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def database_path(self) -> Path:
        database_target = self.database_url.removeprefix("sqlite:///")
        path = Path(database_target)
        return path if path.is_absolute() else ROOT_DIR / path


settings = Settings()
settings.prepare_directories()
