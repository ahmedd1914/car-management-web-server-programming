from fastapi.logger import logger
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, date, timedelta

from app.models.garage import Garage
from app.models.maintenance import MaintenanceRequest


def get_requests_per_month(db: Session, garage_id: int, start_month: datetime, end_month: datetime):
    """
    Get the number of maintenance requests per month for a given garage.
    Includes months with zero requests.
    """
    # Validate that start_month and end_month are datetime objects
    if not isinstance(start_month, datetime) or not isinstance(end_month, datetime):
        raise ValueError("start_month and end_month must be datetime objects.")

    # Query for maintenance counts grouped by year and month
    results = (
        db.query(
            extract("year", MaintenanceRequest.scheduled_date).label("year"),
            extract("month", MaintenanceRequest.scheduled_date).label("month"),
            func.count(MaintenanceRequest.id).label("requests")
        )
        .filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduled_date >= start_month.date(),
            MaintenanceRequest.scheduled_date <= end_month.date()
        )
        .group_by(
            extract("year", MaintenanceRequest.scheduled_date),
            extract("month", MaintenanceRequest.scheduled_date)
        )
        .all()
    )

    # Create a dictionary for results
    monthly_counts = {
        f"{int(row.year)}-{int(row.month):02d}": row.requests for row in results
    }

    # Generate all months between start_month and end_month
    all_months = []
    current_date = start_month
    while current_date <= end_month:
        all_months.append(current_date.strftime("%Y-%m"))
        year, month = current_date.year, current_date.month
        if month == 12:
            current_date = datetime(year + 1, 1, 1)
        else:
            current_date = datetime(year, month + 1, 1)

    # Populate the result, including months with zero requests
    monthly_requests = [
        {"month": month, "requests": monthly_counts.get(month, 0)} for month in all_months
    ]

    return monthly_requests

def get_daily_availability_report(db: Session, garage_id: int, start_date: str, end_date: str):
    """ Get the daily availability for a given garage """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Get all dates between start_date and end_date
    all_dates = []
    current_date = start_date
    while current_date <= end_date:
        all_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    results = (
        db.query(
            MaintenanceRequest.scheduled_date.label("date"),
            func.count(MaintenanceRequest.id).label("requests")
        )
            .filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduled_date.between(start_date, end_date)
        )
            .group_by(MaintenanceRequest.scheduled_date)
            .all()
    )

    requests_dict = {row.date: row.requests for row in results}

    daily_report = []
    for date in all_dates:
        requests = requests_dict.get(date, 0)
        available_capacity = garage.capacity - requests
        daily_report.append({
            "date": date,
            "requests": requests,
            "availableCapacity": available_capacity
        })

    return daily_report