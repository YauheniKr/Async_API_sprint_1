from functools import lru_cache
from typing import Optional, List
from uuid import UUID

import elasticsearch
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FullFilm, BaseFilm
from models.genre import Genre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic)):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[FullFilm]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        # film = await self._film_from_cache(film_id)
        film = None
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            try:
                film = await self._get_film_from_elastic(film_id)
            except elasticsearch.exceptions.NotFoundError:
                film = None
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)
        return film

    async def _search_film_in_elastic(self, query, **kwargs):
        page_number = int(kwargs.get('page_number'))
        size = int(kwargs.get('size'))
        start_number = (page_number - 1) * size
        end_number = page_number * size
        s = Search(index='movies').query("multi_match", query=query, fuzziness="auto")[start_number:end_number]
        docs = await self.elastic.search(index=s._index, body=s.to_dict())
        out = [BaseFilm(**doc['_source']) for doc in docs['hits']['hits']]
        return out

    async def _get_film_from_elastic(self, film_id: str) -> Optional[FullFilm]:
        doc = await self.elastic.get('movies', film_id)
        genre_request = await self._get_genres_by_name(doc['_source']['genre'])
        genres_list = [Genre(**genre['hits']['hits'][0]['_source']) for genre in genre_request]
        doc['_source'].update({'genre': genres_list})
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

    async def _get_genres_by_name(self, genre_names_list: List[str]) -> List[dict]:
        s_list = [Search(index='genre').query("match", name=name) for name in genre_names_list]
        out = [await self.elastic.search(index=s._index, body=s.to_dict()) for s in s_list]
        return out

    async def _get_genres_by_uuid(self, genre_uuid: UUID) -> dict:
        s_request = Search(index='genre').query("match", id=genre_uuid)
        response_genre = await self.elastic.search(index=s_request._index, body=s_request.to_dict())
        return response_genre

    async def _get_film_list_from_elastic(self, **kwargs) -> List[BaseFilm]:
        page_number = int(kwargs.get('page_number'))
        size = int(kwargs.get('size'))
        start_number = (page_number - 1) * size
        end_number = page_number * size
        s = Search(index='movies').query("match_all").sort(kwargs.get('sort'))[start_number:end_number]
        filter_regex = kwargs.get('filter_request')
        if filter_regex:
            genre_name = await self._get_genres_by_uuid(filter_regex)
            genre_name = genre_name['hits']['hits'][0]['_source']['name']
            s = s.filter('term', genre=genre_name)
        docs = await self.elastic.search(index=s._index, body=s.to_dict())
        out = [BaseFilm(**doc['_source']) for doc in docs['hits']['hits']]
        return out

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
