from typing import List

from fastapi import APIRouter, Query

from src.models.film import BaseFilm
from src.models.person import Person

router = APIRouter()


@router.get('/search', response_model=List[Person])
async def search_persons(
    query: str, page_number=Query(default=1, alias='page[number]'), size=Query(default=50, alias='page[size]')
):
    pass


@router.get('/{id:uuid}', response_model=Person)
async def get_persons_by_id(
    id: str
):
    pass


@router.get('/{id:uuid}/film', response_model=List[BaseFilm])
async def get_person_films(id: str):
    pass
