from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.genre import Genre

router = APIRouter()

@router.get('/', response_model=List[Genre])
async def get_genres():
    pass

@router.get('/{id:uuid}', response_model=Genre)
async def get_genre_by_id(id: str):
    pass
