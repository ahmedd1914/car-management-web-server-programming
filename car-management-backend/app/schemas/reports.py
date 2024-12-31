from pydantic import BaseModel


class DailyAvailabilityResponse(BaseModel):
    date: str
    requests: int
    available_capacity: int

    class Config:
        orm_mode = True



# class YearMonth(BaseModel):
#     year: int
#     monthValue: int
#
# class MonthlyReportResponse(BaseModel):
#     year_month: str
#     requests: int
