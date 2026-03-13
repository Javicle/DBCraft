from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SYSTEM_DATABASE_PATH = Path(BASE_DIR / "data/system/dbcraft.db")


class Settings(BaseSettings):
    DATABASE_URL: str
    SYSTEM_DATABASE_URL: str = f"sqlite:///{SYSTEM_DATABASE_PATH}"
    model_config = SettingsConfigDict(env_file=(".env"), env_file_encoding="utf-8")


try:
    settings = Settings()  # type: ignore
except ValidationError as exc:
    raise ValueError("Not found env file") from exc


if __name__ == "__main__":
    if SYSTEM_DATABASE_PATH.exists():
        print("SYSTEM_DATABASE_PATH.exists существует")
    else:
        print("ОТСУТВУЕТ.")
