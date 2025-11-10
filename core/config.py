from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    image_path: str
    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


def load_config(path: Path | None = None) -> Settings:
    conf = Settings(_env_file=path) if path else Settings()
    return conf
