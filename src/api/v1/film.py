from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import UUID4, BaseModel, Field

from src.api.v1.genre import Genre
from src.models.person import PersonBase
from src.services.film import FilmService

router = APIRouter()


class FilmBase(BaseModel):
    uuid: UUID4
    title: str
    imdb_rating: float


class Film(FilmBase):
    description: Optional[str] = Field(default_factory=str)
    genre: list[Genre]
    actors: list[PersonBase]
    writers: Optional[list[PersonBase]] = Field(default_factory=list)
    directors: Optional[list[PersonBase]] = Field(default_factory=list)


@router.get('/', response_model=list[FilmBase])
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
    films_out = [FilmBase(uuid=film.id, **film.__dict__) for film in films]
    return films_out


@router.get('/search', response_model=list[FilmBase])
async def search_films(
        query: str,
        film_service: FilmService = Depends(),
        page_number=Query(default=1, alias='page[number]'),
        size=Query(default=50, alias='page[size]')
):
    films = await film_service.search_film_in_elastic(query=query, page_number=page_number, size=size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    films_out = [FilmBase(uuid=film.id, **film.__dict__) for film in films]
    return films_out


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends()) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    genre_out = [Genre(uuid=genre.id, name=genre.name) for genre in film.genre]
    del(film.__dict__['genre'])
    film_out = Film(uuid=film.id, genre=genre_out, **film.__dict__)
    return film_out
