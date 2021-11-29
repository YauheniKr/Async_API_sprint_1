from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import UUID4

from src.models.film import BaseFilm
from src.models.person import Person
from src.services.person import PersonService

router = APIRouter()


@router.get('/search', response_model=list[Person])
async def search_persons(
    query: str,
    page_number: int = Query(default=1, alias='page[number]'),
    page_size: int = Query(default=50, alias='page[size]'),
    service: PersonService = Depends(),
):
    person = await service.search_person(query, page_number, page_size)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found for this query')
    return person


@router.get('/{id:uuid}', response_model=Person)
async def get_persons_by_id(
    id: UUID4,
    service: PersonService = Depends(),
):
    person = await service.get_person_by_id(id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return person


@router.get('/{id:uuid}/film', response_model=list[BaseFilm])
async def get_person_films(
    id: UUID4,
    service: PersonService = Depends(),
):
    person_films = await service.get_person_films_by_person_id(id)
    if not person_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return person_films
