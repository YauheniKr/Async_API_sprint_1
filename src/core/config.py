from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings

from src.core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME: str = 'movies'

    # Настройки Redis
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    # Настройки Elasticsearch
    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: int = 9200

    # Корень проекта
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    GENRE_CACHE_EXPIRE_IN_SECONDS: int = 5 * 60
    PERSON_CACHE_EXPIRE_IN_SECONDS: int = 5 * 60

    class Config:
        case_sensitive = True


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
