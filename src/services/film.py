from typing import Optional
from uuid import UUID

import elasticsearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from services.helpers import get_pagination_param
from src.db.elastic import get_elastic
from src.models.film import BaseFilm, FullFilm
from src.services.genre import GenreService
from src.services.redis import RedisBaseClass

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: RedisBaseClass = Depends(), elastic: AsyncElasticsearch = Depends(get_elastic)):
        self.elastic = elastic
        self.redis = redis

    async def get_by_id(self, film_id: str) -> Optional[FullFilm]:
        s = Search(index='movies').query("match", id=film_id)
        film = await self._get_data(s)
        film = film[0]['_source']
        film_out = FullFilm(**film)
        return film_out

    async def _get_data(self, s: Search):
        s_dict = s.to_dict()
        index = s._index[0]
        key = str(s_dict)
        film = await self.redis.get_data_from_cache(key, index)
        if not film:
            try:
                film = await self._get_film_from_elastic(s)
            except elasticsearch.exceptions.NotFoundError:
                film = None
            if not film:
                return None
            await self.redis.put_data_to_cache(film, key, index, FILM_CACHE_EXPIRE_IN_SECONDS)
        return film

    async def get_film_list(self, sort: str, page_number: str, size: str, filter_request: UUID) -> list[BaseFilm]:
        start_number, end_number = get_pagination_param(int(page_number), int(size))
        s = Search(index='movies').query("match_all").sort(sort)[start_number:end_number]
        if filter_request:
            genre_service = GenreService(self.redis, self.elastic)
            genre_name = await genre_service.get_genre_by_id(filter_request)
            s = s.filter('term', genre=genre_name.name)
        films = await self._get_data(s)
        films_out = [BaseFilm(**film['_source']) for film in films]
        return films_out

    async def search_film_in_elastic(self, query: str, page_number: str, size: str) -> list[BaseFilm]:
        start_number, end_number = get_pagination_param(int(page_number), int(size))
        s = Search(index='movies').query("multi_match", query=query, fuzziness="auto")[start_number:end_number]
        films = await self._get_data(s)
        films_out = [BaseFilm(**film['_source']) for film in films]
        return films_out

    async def _get_film_from_elastic(self, s: Search) -> Optional[FullFilm]:
        doc = await self.elastic.search(index=s._index, body=s.to_dict())
        doc = doc['hits']['hits']
        return doc
