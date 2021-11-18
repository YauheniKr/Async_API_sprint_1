from typing import List

from pydantic import UUID4, Field

from models.genre import Genre
from models.person import PersonBase
from src.models.base import BaseModel


class BaseFilm(BaseModel):
    id: UUID4 = Field(alias="uuid")
    title: str
    imdb_rating: str


class FullFilm(BaseFilm):
    description: str
    genre: List[Genre]
    actors: List[PersonBase]
    writers: List[PersonBase]
    directors: List[PersonBase]
