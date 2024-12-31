from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, class_mapper
from app.cruds.reports import get_monthly_requests_report
from app.models.database import SessionLocal
from app.schemas.maintenance import (
    MaintenanceRequestResponse,
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate,
)
from app.cruds import maintenance as maintenance_crud


router = APIRouter()

def sqlalchemy_to_dict(model_instance):
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

@router.get("/maintenance", response_model=list[MaintenanceRequestResponse])
def list_maintenance_requests(carId: int = None, garageId: int = None, startDate: str = None, endDate: str = None,
                              db: Session = Depends(get_db)):
    requests = maintenance_crud.get_maintenance_requests(db=db, car_id=carId, garage_id=garageId, start_date=startDate,
                                                         end_date=endDate)

    return [sqlalchemy_to_dict(request) for request in requests]


@router.get("/maintenance/{id:int}", response_model=MaintenanceRequestResponse)
def get_maintenance_request(id: int, db: Session = Depends(get_db)):

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

    deleted_request = maintenance_crud.delete_maintenance_request(db=db, request_id=id)
    if not deleted_request:
        raise HTTPException(status_code=404, detail="Maintenance request not found.")
    return {"message": f"Maintenance request with ID {id} deleted successfully."}


@router.get("/monthlyRequestsReport")
def monthly_requests_report(
    garage_id: int,
    startMonth: str,
    endMonth: str,
    db: Session = Depends(get_db),
):

    try:
        start_date = datetime.strptime(startMonth, "%Y-%m").date()
        end_date = datetime.strptime(endMonth, "%Y-%m").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM format.")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start month cannot be after end month.")

    # Generate the report
    report = get_monthly_requests_report(db, garage_id, start_date, end_date)

    return report
