from pydantic import UUID4

from src.models.base import BaseModel


class Genre(BaseModel):
    id: UUID4
    name: str
