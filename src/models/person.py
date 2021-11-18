from typing import List

from pydantic import UUID4, Field

from src.models.base import BaseModel


class PersonBase(BaseModel):
    id: UUID4 = Field(alias="uuid")
    name: str = Field(alias="full_name")


class Person(PersonBase):
    role: str
    film_ids: List[UUID4]
