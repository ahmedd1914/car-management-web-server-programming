from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from app.cruds import garage as garage_crud
from app.cruds.reports import get_daily_availability_report, get_monthly_requests_report

from app.models.database import SessionLocal
from app.schemas.garage import (
    GarageCreate,
    GarageResponse,
    GarageUpdate,

)

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

@router.get("/{id:int}", response_model=GarageResponse)
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


@router.get("/dailyAvailabilityReport")
def daily_availability_report(
    garage_id: str = Query(..., alias="garageId"),  # Expect `garageId` as a string from frontend
    start_date: str = Query(..., alias="startDate"),  # Expect `startDate` as a string
    end_date: str = Query(..., alias="endDate"),  # Expect `endDate` as a string
    db: Session = Depends(get_db),
):
    """
    Generate a daily availability report for a garage.
    """

    # Step 1: Convert `garageId` to integer
    try:
        garage_id = int(garage_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid garageId. It must be an integer."
        )

    # Step 2: Parse `startDate` and `endDate`
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Expected YYYY-MM-DD. Error: {e}"
        )

    # Step 3: Validate that start_date <= end_date
    if start_date_parsed > end_date_parsed:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date."
        )

    # Step 4: Generate the report
    try:
        report = get_daily_availability_report(db, garage_id, start_date_parsed, end_date_parsed)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report. Please try again later. Error: {e}"
        )

    return report

@router.delete("/{id}", response_model=dict)
def delete_garage_endpoint(id: int, db: Session = Depends(get_db)):
    deleted_garage = garage_crud.delete_garage(db=db, garage_id=id)
    if not deleted_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return {"message": f"Garage with ID {id} deleted successfully"}

