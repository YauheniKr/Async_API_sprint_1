from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from models.film import BaseFilm
from services.film import FilmService

router = APIRouter()


@router.get('/', response_model=List[BaseFilm])
async def get_films(
    sort: str, page_number=Query(default=1, alias='page[number]'), size=Query(default=50, alias='page[size]')
):
    pass


@router.get('/search', response_model=List[BaseFilm])
async def search_films(
    query: str, page_number=Query(default=1, alias='page[number]'), size=Query(default=50, alias='page[size]')
):
    pass


# Внедряем FilmService с помощью Depends(get_film_service)
# TODO тут response_model должен быть FullFilm
@router.get('/{film_id}', response_model=BaseFilm)
async def film_details(film_id: str, film_service: FilmService = Depends()) -> BaseFilm:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return film
