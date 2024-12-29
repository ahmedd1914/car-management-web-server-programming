from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.garage import GarageResponse


class CarBase(BaseModel):
    make: str
    model: str
    production_year: int = Field(..., alias="productionYear")  # Added alias for compatibility
    license_plate: str = Field(..., alias="licensePlate")  # Added alias for compatibility


class CarCreate(CarBase):
    garage_ids: List[int] = Field(..., alias="garageIds")  # Added alias for compatibility


class CarUpdate(BaseModel):
    make: Optional[str]
    model: Optional[str]
    production_year: Optional[int] = Field(None, alias="productionYear")  # Added alias for compatibility
    license_plate: Optional[str] = Field(None, alias="licensePlate")  # Added alias for compatibility
    garage_ids: Optional[List[int]] = Field(None, alias="garageIds")  # Added alias for compatibility


class CarResponse(CarBase):
    id: int
    garages: List[GarageResponse]  # Nested GarageResponse model

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # Allow both `licensePlate` and `license_plate`
