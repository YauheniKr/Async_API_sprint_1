from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FullFilm

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[FullFilm]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[FullFilm]:
        doc = await self.elastic.get('movies', film_id)
        return FullFilm(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[FullFilm]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = FullFilm.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: FullFilm):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(str(film.id), film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic),
                     ) -> FilmService:
    return FilmService(redis, elastic)
