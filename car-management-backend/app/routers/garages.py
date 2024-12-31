from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.cruds import garage as garage_crud
from app.cruds.reports import get_daily_availability_report
from app.models.database import SessionLocal
from app.schemas.garage import (
    GarageCreate,
    GarageResponse,
    GarageUpdate,

)
from app.schemas.reports import DailyAvailabilityResponse

router = APIRouter()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=GarageResponse)
def create_garage_endpoint(garage: GarageCreate, db: Session = Depends(get_db)):
    try:
        return garage_crud.create_garage(db=db, garage=garage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[GarageResponse])
def list_garages_endpoint(city: Optional[str] = None, db: Session = Depends(get_db)):
    return garage_crud.get_garages(db=db, city=city)


@router.get("/{id}", response_model=GarageResponse)
def get_garage_endpoint(id: int, db: Session = Depends(get_db)):
    garage = garage_crud.get_garage(db=db, garage_id=id)
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return garage


@router.put("/{id}", response_model=GarageResponse)
def update_garage_endpoint(id: int, garage: GarageUpdate, db: Session = Depends(get_db)):
    updated_garage = garage_crud.update_garage(db=db, garage_id=id, garage=garage)
    if not updated_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return updated_garage


@router.get("/dailyAvailabilityReport", response_model=List[DailyAvailabilityResponse])
def daily_availability_report(
    garage_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
):
    if not garage_id or not start_date or not end_date:
        raise HTTPException(status_code=400, detail="All parameters are required.")

    # Parse dates and validate format
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Validate date range
    if start_date_parsed > end_date_parsed:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

    # Fetch data from the database
    data = get_daily_availability_report(db, garage_id, start_date, end_date)

    # Handle no data found case
    if not data:
        raise HTTPException(status_code=404, detail="No data found for the given parameters.")

    return data


@router.delete("//{id}", response_model=dict)
def delete_garage_endpoint(id: int, db: Session = Depends(get_db)):
    deleted_garage = garage_crud.delete_garage(db=db, garage_id=id)
    if not deleted_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return {"message": f"Garage with ID {id} deleted successfully"}

