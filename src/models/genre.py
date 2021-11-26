from pydantic import UUID4, Field

from src.models.base import BaseModel


class Genre(BaseModel):
    id: UUID4 = Field(alias="uuid")
    name: str
