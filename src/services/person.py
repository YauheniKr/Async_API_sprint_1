import elasticsearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Q, Search
from fastapi import Depends
from pydantic import UUID4

from services.helpers import get_pagination_param
from src.core.config import settings
from src.db.elastic import get_elastic
from src.models.person import Person
from src.services.redis import RedisBaseClass


class PersonService:
    def __init__(self, redis: RedisBaseClass = Depends(), elastic: AsyncElasticsearch = Depends(get_elastic)):
        self.redis = redis
        self.elastic = elastic

        self.es_index = "person"

    async def get_person_by_id(self, person_id) -> Person:
        elastic_request = Search(index=self.es_index).query("ids", values=[person_id])

        person = await self._get_request_from_cache_or_es(elastic_request)
        films = await self.get_person_films_by_person_id(person_id)
        film_ids = [film["id"] for film in films]
        return Person(**person[0]["_source"], film_ids=film_ids)

    async def search_person(self, query: str, page_number: int, page_size: int) -> list[Person]:
        start_number, end_number = get_pagination_param(int(page_number), int(page_size))
        elastic_request = (
            Search(index=self.es_index).query("multi_match", query=query, fuzziness="auto")[start_number:end_number]
        )
        persons = await self._get_request_from_cache_or_es(elastic_request)
        out_persons = list()
        for p in persons:
            films = await self.get_person_films_by_person_id(p["_source"]["id"])
            film_ids = [f["id"] for f in films]
            person = Person(**p["_source"], film_ids=film_ids)
            out_persons.append(person)
        return out_persons

    async def get_person_films_by_person_id(self, person_id: UUID4):
        search_query = Search(index="movies").query("bool", minimum_should_match=1, should=[
            Q("nested", path="actors", query=Q("match", actors__id=str(person_id))),
            Q("nested", path="writers", query=Q("match", writers__id=str(person_id))),
            Q("nested", path="directors", query=Q("match", directors__id=str(person_id))),
        ])
        films_from_elastic = await self.elastic.search(index='movies', body=search_query.to_dict())
        return [film["_source"] for film in films_from_elastic["hits"]["hits"]]

    async def _get_request_from_cache_or_es(self, search_query: Search):
        index = search_query._index[0]
        result = await self.redis.get_data_from_cache(str(search_query.to_dict()), index)
        if not result:
            try:
                result = await self._get_person_from_elastic(search_query)
            except elasticsearch.exceptions.NotFoundError:
                return None
            if not result:
                return None
            await self.redis.put_data_to_cache(result, str(search_query.to_dict()), index,
                                               settings.PERSON_CACHE_EXPIRE_IN_SECONDS)
        return result

    async def _get_person_from_elastic(self, search: Search):
        document = await self.elastic.search(index=self.es_index, body=search.to_dict())
        document = document['hits']['hits']
        return document
