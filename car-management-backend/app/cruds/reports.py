from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.models.garage import Garage
from app.models.maintenance import MaintenanceRequest



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



def get_daily_availability_report(db: Session, garage_id: int, start_date: datetime.date, end_date: datetime.date):
    """
    Generate the daily availability report for the given date range.
    """
    # Fetch the garage's total capacity
    garage = db.query(Garage).filter(Garage.id == garage_id).first()
    if not garage:
        raise HTTPException(
            status_code=404,
            detail=f"Garage with id {garage_id} not found."
        )
    total_capacity = garage.capacity  # Use the `capacity` field from the Garage model

    # Query maintenance requests grouped by date
    daily_requests = (
        db.query(
            MaintenanceRequest.scheduled_date,
            func.count(MaintenanceRequest.id).label("requests")
        )
        .filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduled_date >= start_date,
            MaintenanceRequest.scheduled_date <= end_date,
        )
        .group_by(MaintenanceRequest.scheduled_date)
        .order_by(MaintenanceRequest.scheduled_date)
        .all()
    )

    # Create a dictionary of requests per day
    report = {}
    for request in daily_requests:
        report[request.scheduled_date] = request.requests

    # Generate the report directly as a list of dictionaries
    final_report = []
    current_date = start_date
    while current_date <= end_date:
        requests = report.get(current_date, 0)
        available_capacity = max(0, total_capacity - requests)  # Calculate available capacity

        # Add dictionary to the final report
        final_report.append({
            "date": current_date.isoformat(),
            "requests": requests,
            "availableCapacity": available_capacity  # Use camelCase directly
        })
        current_date += timedelta(days=1)

    return final_report

