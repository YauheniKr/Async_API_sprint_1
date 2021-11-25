from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from services.genre import GenreService
from src.models.genre import Genre

router = APIRouter()


@router.get('/', response_model=List[Genre])
async def get_genres(genre_service: GenreService = Depends()):
    genres = await genre_service.get_genre_list()
    if not genres:
        return []
    return genres


@router.get('/{genre_id:uuid}', response_model=Genre)
async def get_genre_by_id(genre_id: UUID4, genre_service: GenreService = Depends()):
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre
