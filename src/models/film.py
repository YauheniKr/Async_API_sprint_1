from typing import Optional

from pydantic import UUID4, Field

from src.models.base import BaseModel
from src.models.genre import Genre
from src.models.person import PersonBase


class BaseFilm(BaseModel):
    id: UUID4
    title: str
    imdb_rating: float


class FullFilm(BaseFilm):
    description: Optional[str] = None
    genre: list[Genre]
    actors: list[PersonBase]
    writers: Optional[list[PersonBase]] = Field(default_factory=list)
    directors: Optional[list[PersonBase]] = Field(default_factory=list)
