from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.models.garage import Garage
from app.models.maintenance import MaintenanceRequest
from app.schemas.reports import DailyAvailabilityResponse


def get_monthly_requests_report(
        db: Session,
        garage_id: int,
        start_date: datetime.date,
        end_date: datetime.date,
):
    """Generate the monthly report for a given garage within a date range"""

    # Adjust end_date to include the entire last day of the month
    end_date = datetime(end_date.year, end_date.month, 1).date()
    next_month = (end_date.month % 12) + 1
    next_year = end_date.year + (end_date.month // 12)
    end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)

    # Query maintenance requests within the date range
    maintenances = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.garage_id == garage_id,
        MaintenanceRequest.scheduled_date >= start_date,
        MaintenanceRequest.scheduled_date <= end_date,
    ).all()

    report = {}
    for maintenance in maintenances:
        scheduled_date = maintenance.scheduled_date
        if scheduled_date:
            # Combine year and month into a single string "yyyy-mm"
            year_month = f"{scheduled_date.year}-{str(scheduled_date.month).zfill(2)}"
        else:
            # Skip entries without a valid scheduled_date
            continue

        # Aggregate requests by yearMonth
        report[year_month] = report.get(year_month, 0) + 1

    # Format the response with yearMonth as a string
    formatted_report = [
        {"yearMonth": year_month, "requests": count}
        for year_month, count in sorted(report.items())  # Sort by yearMonth
    ]

    return formatted_report


def get_daily_availability_report(
    db: Session, garage_id: int, start_date: str, end_date: str
) -> List[DailyAvailabilityResponse]:
    # Parse the start_date and end_date
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if start_date_parsed > end_date_parsed:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

    # Query the database for daily availability
    query_result = (
        db.query(
            MaintenanceRequest.garage_id,
            MaintenanceRequest.scheduled_date.label("date"),
            db.func.count(MaintenanceRequest.id).label("requests"),
            (Garage.capacity - db.func.count(MaintenanceRequest.id)).label("available_capacity"),
        )
        .join(Garage, MaintenanceRequest.garage_id == Garage.id)
        .filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduled_date >= start_date_parsed,
            MaintenanceRequest.scheduled_date <= end_date_parsed,
        )
        .group_by(MaintenanceRequest.garage_id, MaintenanceRequest.scheduled_date, Garage.capacity)
        .all()
    )

    # Convert query result into Pydantic models
    return [
        DailyAvailabilityResponse(
            garage_id=row.garage_id,
            date=row.date.strftime("%Y-%m-%d"),  # Convert date to string format
            requests=row.requests,
            available_capacity=row.available_capacity,
        )
        for row in query_result
    ]
