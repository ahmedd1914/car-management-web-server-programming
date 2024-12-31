from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceRequest
from app.models.car import Car
from app.models.garage import Garage
from app.schemas.maintenance import MaintenanceRequestCreate, MaintenanceRequestUpdate
from app.cruds.utils import get_or_404


def create_maintenance_request(db: Session, maintenance_request: MaintenanceRequestCreate):

    # Validate the scheduled date
    if maintenance_request.scheduled_date < date.today():
        raise HTTPException(status_code=400, detail="Scheduled date cannot be in the past.")

    # Ensure the Car exists
    car = get_or_404(db, Car, maintenance_request.car_id, f"Car with ID {maintenance_request.car_id} not found.")

    # Ensure the Garage exists
    garage = get_or_404(db, Garage, maintenance_request.garage_id, f"Garage with ID {maintenance_request.garage_id} not found.")

    # Check if the garage is full on the scheduled date
    if is_garage_full(db, maintenance_request.garage_id, maintenance_request.scheduled_date):
        raise HTTPException(
            status_code=400,
            detail=f"Garage with ID {maintenance_request.garage_id} is at full capacity on {maintenance_request.scheduled_date}.",
        )

    # Create the maintenance request
    db_request = MaintenanceRequest(
        car_id=maintenance_request.car_id,
        car_name=f"{car.make} {car.model}",
        service_type=maintenance_request.service_type,
        scheduled_date=maintenance_request.scheduled_date,
        garage_id=maintenance_request.garage_id,
        garage_name=garage.name
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request



def get_maintenance_request(db: Session, request_id: int):
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()


def get_maintenance_requests(
    db: Session,
    car_id: int = None,
    garage_id: int = None,
    start_date: date = None,
    end_date: date = None
):
    query = db.query(MaintenanceRequest)

    # Apply filters
    if car_id:
        query = query.filter(MaintenanceRequest.car_id == car_id)
    if garage_id:
        query = query.filter(MaintenanceRequest.garage_id == garage_id)
    if start_date:
        query = query.filter(MaintenanceRequest.scheduled_date >= start_date)
    if end_date:
        query = query.filter(MaintenanceRequest.scheduled_date <= end_date)

    return query.all()



def update_maintenance_request(db: Session, request_id: int, maintenance_request: MaintenanceRequestUpdate):
    # Retrieve the existing request
    db_request = get_or_404(db, MaintenanceRequest, request_id, "Maintenance request not found.")

    # If garage_id was provided, validate the garage
    if maintenance_request.garage_id:
        garage = get_or_404(db, Garage, maintenance_request.garage_id, "Garage not found")
        db_request.garage_id = garage.id
        db_request.garage_name = garage.name

    # If car_id was provided, validate the car
    if maintenance_request.car_id:
        car = get_or_404(db, Car, maintenance_request.car_id, "Car not found")
        db_request.car_id = car.id
        db_request.car_name = f"{car.make} {car.model}"

    # If scheduled_date was provided, validate it
    if maintenance_request.scheduled_date:
        if maintenance_request.scheduled_date < date.today():
            raise HTTPException(status_code=400, detail="Scheduled date cannot be in the past.")
        db_request.scheduled_date = maintenance_request.scheduled_date

    # If service_type was provided, update it
    if maintenance_request.service_type:
        db_request.service_type = maintenance_request.service_type

    # Now ALWAYS check the capacity based on the final db_request.garage_id and db_request.scheduled_date
    if is_garage_full(db, db_request.garage_id, db_request.scheduled_date):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Garage '{db_request.garage_name}' is at full capacity for {db_request.scheduled_date}. "
            ),
        )

    db.commit()
    db.refresh(db_request)
    return db_request



def delete_maintenance_request(db: Session, request_id: int):
    db_request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if db_request:
        db.delete(db_request)
        db.commit()
        return db_request
    return None


def is_garage_full(db: Session, garage_id: int, scheduled_date: date) -> bool:

    # Retrieve the garage to check its capacity
    garage = get_or_404(db, Garage, garage_id, f"Garage with ID {garage_id} not found.")

    # Count the number of maintenance requests scheduled for the specific date
    scheduled_requests_count = (
        db.query(MaintenanceRequest)
        .filter(
            MaintenanceRequest.garage_id == garage_id,
            MaintenanceRequest.scheduled_date == scheduled_date
        )
        .count()
    )

    # Check if the number of requests exceeds or matches the garage capacity
    return scheduled_requests_count >= garage.capacity
