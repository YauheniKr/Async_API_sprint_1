from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4, BaseModel

from src.services.genre import GenreService

router = APIRouter()


class Genre(BaseModel):
    uuid: UUID4
    name: str


@router.get('/', response_model=list[Genre])
async def get_genres(genre_service: GenreService = Depends()):
    genres = await genre_service.get_genre_list()
    if not genres:
        return []
    genres = [Genre(uuid=genre.id, name=genre.name) for genre in genres]
    return genres


@router.get('/{genre_id:uuid}', response_model=Genre)
async def get_genre_by_id(genre_id: UUID4, genre_service: GenreService = Depends()):
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    genre = Genre(uuid=genre.id, name=genre.name)
    return genre
