import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

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

logging.basicConfig(level=logging.INFO)
@router.get("/garages/dailyAvailabilityReport")
def daily_availability_report(
    garage_id: str = Query(..., alias="garageId"),  # Expect `garageId` as a string from frontend
    start_date: str = Query(..., alias="startDate"),  # Expect `startDate` as a string
    end_date: str = Query(..., alias="endDate"),  # Expect `endDate` as a string
    db: Session = Depends(get_db),
):
    """
    Generate a daily availability report for a garage.
    """

    # Log raw parameters
    logging.info(f"Received query params: garageId={garage_id}, startDate={start_date}, endDate={end_date}")

    # Step 1: Convert `garageId` to integer
    try:
        garage_id = int(garage_id)
        logging.info(f"Parsed garageId: {garage_id}")
    except ValueError as e:
        logging.error(f"Invalid garageId. Must be an integer. Error: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid garageId. It must be an integer."
        )

    # Step 2: Parse `startDate` and `endDate`
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
        logging.info(f"Parsed dates: startDate={start_date_parsed}, endDate={end_date_parsed}")
    except ValueError as e:
        logging.error(f"Invalid date format. Expected YYYY-MM-DD. Error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Expected YYYY-MM-DD. Error: {e}"
        )

    # Step 3: Validate that start_date <= end_date
    if start_date_parsed > end_date_parsed:
        logging.error(f"Start date {start_date_parsed} is after end date {end_date_parsed}")
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date."
        )

    # Step 4: Generate the report
    try:
        logging.info(f"Generating report for garageId={garage_id}, startDate={start_date_parsed}, endDate={end_date_parsed}")
        report = get_daily_availability_report(db, garage_id, start_date_parsed, end_date_parsed)
        logging.info(f"Generated report: {report}")
    except Exception as e:
        logging.error(f"Error generating report. Error: {e}")
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

