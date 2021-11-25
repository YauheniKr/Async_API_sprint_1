from typing import List, Optional

from pydantic import UUID4, Field

from src.models.base import BaseModel
from src.models.genre import Genre
from src.models.person import PersonBase


class BaseFilm(BaseModel):
    id: UUID4 = Field(alias="uuid")
    title: str
    imdb_rating: float = Field(alias='rating')


class FullFilm(BaseFilm):
    description: Optional[str] = None
    genre: List[Genre]
    actors: List[PersonBase]
    writers: Optional[List[PersonBase]] = []
    directors: Optional[List[PersonBase]] = []
