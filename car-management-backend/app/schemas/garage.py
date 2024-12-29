from pydantic import BaseModel, Field
from typing import Optional


class GarageBase(BaseModel):
    name: str
    location: str
    city: str
    capacity: int


class GarageCreate(GarageBase):
    pass


class GarageUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    city: Optional[str]
    capacity: Optional[int]


class GarageResponse(GarageBase):
    id: int

    class Config:
        orm_mode = True
