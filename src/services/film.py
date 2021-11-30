from typing import Optional, Union
from uuid import UUID

import elasticsearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search, Q
from fastapi import Depends

from services.helpers import get_pagination_param
from src.db.elastic import get_elastic
from src.models.film import BaseFilm, FullFilm
from src.services.redis import RedisBaseClass

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: RedisBaseClass = Depends(), elastic: AsyncElasticsearch = Depends(get_elastic)):
        self.elastic = elastic
        self.redis = redis

    async def get_by_id(self, film_id: str) -> Union[FullFilm, None]:
        s = Search(index='movies').query("match", id=film_id)
        film = await self._get_data(s)
        if film is None:
            return None
        film = film[0]['_source']
        film_out = FullFilm(**film)
        return film_out

    async def _get_data(self, s: Search) -> Union[dict, list, None]:
        s_dict = s.to_dict()
        index = s._index[0]
        key = str(s_dict)
        data = await self.redis.get_data_from_cache(key, index)
        if not data:
            try:
                data = await self._get_film_from_elastic(s)
            except elasticsearch.exceptions.NotFoundError:
                data = None
            if not data:
                return None
            await self.redis.put_data_to_cache(data, key, index, FILM_CACHE_EXPIRE_IN_SECONDS)
        return data


    @staticmethod
    def _get_pagination_param(page_number: str, size: str) -> tuple:
        page_number = int(page_number)
        size = int(size)
        start_number = (page_number - 1) * size
        end_number = page_number * size
        return start_number, end_number

    async def get_film_list(self, sort: str, page_number: str, size: str,
                            filter_request: UUID) -> Union[list[BaseFilm], None]:
        start_number, end_number = self._get_pagination_param(page_number, size)

        s = Search(index='movies').query("match_all").sort(sort)[start_number:end_number]
        if filter_request:
            s = Search(index="movies").query("bool", minimum_should_match=1, should=[
                Q("nested", path="genre", query=Q("match", genre__id=str(filter_request)))
            ])
        films = await self._get_data(s)
        if films is None:
            return None
        films_out = [BaseFilm(**film['_source']) for film in films]
        return films_out


    async def search_film_in_elastic(self, query: str, page_number: str, size: str) -> Union[list[BaseFilm], None]:
        start_number, end_number = self._get_pagination_param(page_number, size)
        s = Search(index='movies').query("multi_match", query=query, fuzziness="auto")[start_number:end_number]
        films = await self._get_data(s)
        if films is None:
            return None
        films_out = [BaseFilm(**film['_source']) for film in films]
        return films_out

    async def _get_film_from_elastic(self, s: Search) -> Optional[FullFilm]:
        doc = await self.elastic.search(index=s._index, body=s.to_dict())
        doc = doc['hits']['hits']
        return doc
