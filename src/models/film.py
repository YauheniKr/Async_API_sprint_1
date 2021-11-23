from typing import List, Optional

from pydantic import UUID4, Field

from src.models.genre import Genre
from src.models.person import PersonBase
from src.models.base import BaseModel


class BaseFilm(BaseModel):
    id: UUID4 = Field(alias="uuid")
    title: str
    imdb_rating: float


class FullFilm(BaseFilm):
    description: Optional[str]
    # genre: List[Genre]
    actors: List[PersonBase]
    writers: List[PersonBase]
    directors: List[PersonBase]
