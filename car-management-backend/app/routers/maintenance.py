from calendar import isleap
from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, class_mapper, joinedload

from app.models.database import SessionLocal
from app.schemas.maintenance import (
    MaintenanceRequestResponse,
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
)
from app.cruds import maintenance as maintenance_crud, reports as reports_crud
from app.schemas.reports import MonthlyReportResponse, YearMonth

router = APIRouter()

def sqlalchemy_to_dict(model_instance):
    """
    Converts a SQLAlchemy model instance to a dictionary
    while including related fields like `carName` and `garageName`.
    """
    result = {
        column.name: getattr(model_instance, column.name)
        for column in class_mapper(model_instance.__class__).columns
    }

    return {
        "id": result.get("id"),
        "carId": result.get("car_id"),
        "carName": model_instance.car.make if model_instance.car else None,
        "serviceType": result.get("service_type"),
        "scheduledDate": result.get("scheduled_date"),
        "garageId": result.get("garage_id"),
        "garageName": model_instance.garage.name if model_instance.garage else None,
    }

def get_db():
    """
    Dependency to provide a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/maintenance", response_model=MaintenanceRequestResponse)
def create_maintenance_request(
    request: MaintenanceRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Creates a new maintenance request and returns its details.
    """
    if maintenance_crud.is_garage_full(db, request.garage_id, request.scheduled_date):
        raise HTTPException(
            status_code=400,
            detail="Garage is at capacity for the selected date."
        )

    db_maintenance_request = maintenance_crud.create_maintenance_request(
        db=db,
        maintenance_request=request
    )

    if not db_maintenance_request:
        raise HTTPException(status_code=400, detail="Failed to create maintenance request.")

    return sqlalchemy_to_dict(db_maintenance_request)

@router.get("/maintenance", response_model=List[MaintenanceRequestResponse])
def list_maintenance_requests(
    carId: Optional[int] = None,
    garageId: Optional[int] = None,
    scheduledDate: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Print the received query parameters for debugging
    print("DEBUG: Received query params")
    print("carId:", carId)
    print("garageId:", garageId)
    print("scheduledDate:", scheduledDate)

    start_date = None
    end_date = None
      # Parse the `scheduledDate` parameter
    if scheduledDate:
        if "," in scheduledDate:  # Check for a range
            try:
                start_date_str, end_date_str = scheduledDate.split(",")
                start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date range format. Use 'YYYY-MM-DD,YYYY-MM-DD'.")
        else:  # Treat it as a single date
            try:
                start_date = datetime.strptime(scheduledDate.strip(), "%Y-%m-%d").date()
                end_date = start_date  # If a single date is provided, set it as both start and end
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

    print("DEBUG: carId:", carId, "garageId:", garageId, "start_date:", start_date, "end_date:", end_date)

    requests = maintenance_crud.get_maintenance_requests(
        db=db,
        car_id=carId,
        garage_id=garageId,
        start_date=start_date,
        end_date=end_date
    )

    return [sqlalchemy_to_dict(request) for request in requests]

@router.get("/maintenance/{id:int}", response_model=MaintenanceRequestResponse)
def get_maintenance_request(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single maintenance request by ID.
    """
    db_request = maintenance_crud.get_maintenance_request(db=db, request_id=id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Maintenance request not found.")
    return sqlalchemy_to_dict(db_request)

@router.put("/maintenance/{id}", response_model=MaintenanceRequestResponse)
def update_maintenance_request(
    id: int,
    request: MaintenanceRequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates an existing maintenance request and validates garage capacity.
    """
    existing_request = maintenance_crud.get_maintenance_request(db=db, request_id=id)
    if not existing_request:
        raise HTTPException(status_code=404, detail="Maintenance request not found.")

    date_changed = (request.scheduled_date != existing_request.scheduled_date)
    garage_changed = (request.garage_id != existing_request.garage_id)

    if date_changed or garage_changed:
        if maintenance_crud.is_garage_full(db, request.garage_id, request.scheduled_date):
            raise HTTPException(
                status_code=400,
                detail="Garage is at capacity for the selected date."
            )

    updated_request = maintenance_crud.update_maintenance_request(
        db=db,
        request_id=id,
        maintenance_request=request
    )
    if not updated_request:
        raise HTTPException(status_code=404, detail="Failed to update maintenance request.")

    return sqlalchemy_to_dict(updated_request)

@router.delete("/maintenance/{id}", response_model=dict)
def delete_maintenance_request(id: int, db: Session = Depends(get_db)):
    """
    Deletes a maintenance request by ID.
    """
    deleted_request = maintenance_crud.delete_maintenance_request(db=db, request_id=id)
    if not deleted_request:
        raise HTTPException(status_code=404, detail="Maintenance request not found.")
    return {"message": f"Maintenance request with ID {id} deleted successfully."}

@router.get("/maintenance/monthlyRequestsReport", response_model=List[MonthlyReportResponse])
def get_monthly_requests_report(
    garageId: int,
    startMonth: str,
    endMonth: str,
    db: Session = Depends(get_db)
):
    """
    Generates a monthly report for maintenance requests.
    """
    try:
        start_month = datetime.strptime(startMonth, "%Y-%m")
        end_month = datetime.strptime(endMonth, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM'.")

    if start_month > end_month:
        raise HTTPException(status_code=400, detail="Start month cannot be later than end month.")

    requests_per_month = reports_crud.get_requests_per_month(
        db=db,
        garage_id=garageId,
        start_month=start_month,
        end_month=end_month
    )

    response = []
    for year_month, count in requests_per_month.items():
        year, month_value = map(int, year_month.split("-"))
        month_name = datetime(year, month_value, 1).strftime("%B").upper()
        leap_year = isleap(year)

        response.append(
            MonthlyReportResponse(
                yearMonth=YearMonth(
                    year=year,
                    month=month_name,
                    leapYear=leap_year,
                    monthValue=month_value,
                ),
                requests=count,
            )
        )
    return response
