from typing import Optional, List
from uuid import UUID

import elasticsearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from db.elastic import get_elastic
from models.film import FullFilm, BaseFilm
from models.genre import Genre
from .redis import RedisBaseClass

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: RedisBaseClass = Depends(), elastic: AsyncElasticsearch = Depends(get_elastic)):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[FullFilm]:
        s = Search(index='movies').query("match", id=film_id)
        film = await self._get_data(s)
        genre_request = await self._get_genres_by_name(film[0]['_source']['genre'])
        genres_list = [Genre(**genre['_source']) for genre in genre_request[0]['hits']['hits']]
        film = film[0]['_source']
        film.update({'genre': genres_list})
        return film

    async def _get_data(self, s: Search):
        film = await self.redis._get_data_from_cache(s)
        if not film:
            try:
                film = await self._get_film_from_elastic(s)
            except elasticsearch.exceptions.NotFoundError:
                film = None
            if not film:
                return None
            await self.redis._put_data_to_cache(film, s)
        return film

    @staticmethod
    def _get_pagination_param(page_number: str, size: str) -> tuple:
        page_number = int(page_number)
        size = int(size)
        start_number = (page_number - 1) * size
        end_number = page_number * size
        return start_number, end_number

    async def get_film_list(self, sort: str, page_number: str, size: str, filter_request: UUID) -> List[BaseFilm]:
        start_number, end_number = self._get_pagination_param(page_number, size)
        s = Search(index='movies').query("match_all").sort(sort)[start_number:end_number]
        if filter_request:
            genre_name = await self._get_genres_by_uuid(filter_request)
            genre_name = genre_name['hits']['hits'][0]['_source']['name']
            s = s.filter('term', genre=genre_name)
        films = await self._get_data(s)
        films_out = [BaseFilm(**film['_source']) for film in films]
        return films_out

    async def search_film_in_elastic(self, query: str, page_number: str, size: str) -> List[BaseFilm]:
        start_number, end_number = self._get_pagination_param(page_number, size)
        s = Search(index='movies').query("multi_match", query=query, fuzziness="auto")[start_number:end_number]
        films = await self._get_data(s)
        films_out = [BaseFilm(**film['_source']) for film in films]
        return films_out

    #ToDo: Перенести в класс Elastic для использования во всех зарпросах
    async def _get_film_from_elastic(self, s: Search) -> Optional[FullFilm]:
        doc = await self.elastic.search(index=s._index, body=s.to_dict())
        doc = doc['hits']['hits']
        return doc

    # ToDo: Перенести в класс Genre
    async def _get_genres_by_name(self, genre_names_list: List[str]) -> List[dict]:
        s_list = [Search(index='genre').query("match", name=name) for name in genre_names_list]
        out = [await self.elastic.search(index=s._index, body=s.to_dict()) for s in s_list]
        return out

    # ToDo: Перенести в класс Genre
    async def _get_genres_by_uuid(self, genre_uuid: UUID) -> dict:
        s_request = Search(index='genre').query("match", id=genre_uuid)
        response_genre = await self.elastic.search(index=s_request._index, body=s_request.to_dict())
        return response_genre
