from pydantic import BaseModel
from typing import List, Optional
from app.schemas.garage import GarageResponse


class CarBase(BaseModel):
    make: str
    model: str
    production_year: int
    license_plate: str


class CarCreate(CarBase):
    garage_ids: List[int]  # Reference to Garage IDs


class CarUpdate(BaseModel):
    make: Optional[str]
    model: Optional[str]
    production_year: Optional[int]
    license_plate: Optional[str]
    garage_ids: Optional[List[int]]


class CarResponse(CarBase):
    id: int
    garages: List[GarageResponse]  # Nested GarageResponse model

    class Config:
        orm_mode = True
