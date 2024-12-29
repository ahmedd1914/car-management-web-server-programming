from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class MaintenanceRequestCreate(BaseModel):
    car_id: int = Field(..., alias="carId")
    service_type: str = Field(..., alias="serviceType")
    scheduled_date: date = Field(..., alias="scheduledDate")
    garage_id: int = Field(..., alias="garageId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # Allows using both snake_case and camelCase


class MaintenanceRequestUpdate(BaseModel):
    car_id: Optional[int] = Field(None, alias="carId")
    service_type: Optional[str] = Field(None, alias="serviceType")
    scheduled_date: Optional[date] = Field(None, alias="scheduledDate")
    garage_id: Optional[int] = Field(None, alias="garageId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # Allows using both snake_case and camelCase


class MaintenanceRequestResponse(BaseModel):
    id: int
    car_id: int = Field(..., alias="carId")
    car_name: str = Field(..., alias="carName")
    service_type: str = Field(..., alias="serviceType")
    scheduled_date: date = Field(..., alias="scheduledDate")
    garage_id: int = Field(..., alias="garageId")
    garage_name: str = Field(..., alias="garageName")


    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # Allows using both snake_case and camelCase
