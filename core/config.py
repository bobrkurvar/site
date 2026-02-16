import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

COLLECTIONS_PER_PAGE = 20
ITEMS_PER_PAGE = 20


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    api_host: str
    image_port: int
    test_db_name: str
    image_path: str
    secret_key: str
    algorithm: str
    initial_admins: str

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def test_db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.test_db_name}"

    @property
    def image_service_url(self):
        return f"{self.api_host}:{self.image_port}"

    @property
    def initial_admins_list(self):
        try:
            return json.loads(self.initial_admins)
        except Exception:
            return []


def load_config(path: Path | None = None) -> Settings:
    #conf = Settings(_env_file=path) if path else Settings()
    conf = Settings() # type: ignore
    return conf
