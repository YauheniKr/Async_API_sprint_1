from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.film import BaseFilm, FullFilm
from src.services.film import FilmService

router = APIRouter()


@router.get('/', response_model=List[BaseFilm])
async def get_films(
    sort: str,
    film_service: FilmService = Depends(),
    page_number=Query(default=1, alias='page[number]'),
    size=Query(default=50, alias='page[size]'),
    filter_request: Optional[UUID] = Query(None, alias='filter[genre]')
):
    films = await film_service.get_film_list(sort=sort, page_number=page_number, size=size,
                                             filter_request=filter_request)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return films


@router.get('/search', response_model=List[BaseFilm])
async def search_films(
    query: str,
    film_service: FilmService = Depends(),
    page_number=Query(default=1, alias='page[number]'),
    size=Query(default=50, alias='page[size]')
):
    films = await film_service.search_film_in_elastic(query=query, page_number=page_number, size=size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return films


@router.get('/{film_id}', response_model=FullFilm)
async def film_details(film_id: str, film_service: FilmService = Depends()) -> FullFilm:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return film
