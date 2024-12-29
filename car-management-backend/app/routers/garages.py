from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.logger import logger
from sqlalchemy.orm import Session

from app.cruds import garage as garage_crud, reports as reports_crud
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


@router.post("/garages", response_model=GarageResponse)
def create_garage_endpoint(garage: GarageCreate, db: Session = Depends(get_db)):
    try:
        return garage_crud.create_garage(db=db, garage=garage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/garages", response_model=List[GarageResponse])
def list_garages_endpoint(city: Optional[str] = None, db: Session = Depends(get_db)):
    return garage_crud.get_garages(db=db, city=city)


@router.get("/garages/{id}", response_model=GarageResponse)
def get_garage_endpoint(id: int, db: Session = Depends(get_db)):
    garage = garage_crud.get_garage(db=db, garage_id=id)
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return garage


@router.put("/garages/{id}", response_model=GarageResponse)
def update_garage_endpoint(id: int, garage: GarageUpdate, db: Session = Depends(get_db)):
    updated_garage = garage_crud.update_garage(db=db, garage_id=id, garage=garage)
    if not updated_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return updated_garage


@router.delete("/garages/{id}", response_model=dict)
def delete_garage_endpoint(id: int, db: Session = Depends(get_db)):
    deleted_garage = garage_crud.delete_garage(db=db, garage_id=id)
    if not deleted_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return {"message": f"Garage with ID {id} deleted successfully"}


@router.get("/garages/dailyAvailabilityReport", response_model=List[DailyAvailabilityResponse])
def get_daily_availability_report(garage_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):
    report = get_daily_availability_report(db=db, garage_id=garage_id,
                                                             start_date=start_date, end_date=end_date)
    return report