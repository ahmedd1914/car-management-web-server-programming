from pydantic import BaseModel


class DailyAvailabilityResponse(BaseModel):
    date: str
    requests: int
    available_capacity: int

    class Config:
        orm_mode = True


class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    requests: int
