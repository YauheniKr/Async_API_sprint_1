import elasticsearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from src.core.config import settings
from src.db.elastic import get_elastic
from src.models.genre import Genre

from .redis import RedisBaseClass


class GenreService:
    def __init__(self, redis: RedisBaseClass = Depends(), elastic: AsyncElasticsearch = Depends(get_elastic)):
        self.redis = redis
        self.elastic = elastic

        self.es_index = "genre"

    async def get_genre_by_id(self, genre_id):
        elastic_request = Search(index=self.es_index).query("match", id=genre_id)

        genre = await self._get_request_from_cache_or_es(elastic_request)

        return Genre(**genre[0]["_source"])

    async def get_genre_list(self):
        elastic_request = Search(index=self.es_index).query("match_all")[:1000]

        genres = await self._get_request_from_cache_or_es(elastic_request)

        return [Genre(**g["_source"]) for g in genres]

    async def _get_request_from_cache_or_es(self, search_query: Search):
        index = search_query._index[0]
        genre = await self.redis.get_data_from_cache(str(search_query.to_dict()), index)
        if not genre:
            try:
                genre = await self._get_genre_from_elastic(search_query)
            except elasticsearch.exceptions.NotFoundError:
                return None
            if not genre:
                return None
            await self.redis.put_data_to_cache(genre, str(search_query.to_dict()), index,
                                               settings.GENRE_CACHE_EXPIRE_IN_SECONDS)
        return genre

    async def _get_genre_from_elastic(self, search: Search):
        document = await self.elastic.search(index=self.es_index, body=search.to_dict())
        document = document['hits']['hits']
        return document

    async def get_genres_by_name(self, genre_names_list: list[str]) -> list[dict]:
        s_list = [Search(index='genre').query("match", name=name) for name in genre_names_list]
        out = [await self._get_request_from_cache_or_es(s) for s in s_list]
        return out
