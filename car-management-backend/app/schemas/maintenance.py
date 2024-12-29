from datetime import date
from pydantic import BaseModel
from typing import Optional


class MaintenanceRequestCreate(BaseModel):
    car_id: int
    service_type: str
    scheduled_date: date
    garage_id: int

    class Config:
        orm_mode = True


class MaintenanceRequestUpdate(BaseModel):
    car_id: Optional[int]
    service_type: Optional[str]
    scheduled_date: Optional[date]
    garage_id: Optional[int]


class MaintenanceRequestResponse(BaseModel):
    id: int
    car_id: int
    service_type: str
    scheduled_date: date
    garage_id: int

    class Config:
        orm_mode = True
