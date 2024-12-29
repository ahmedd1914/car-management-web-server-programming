from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from app.models.database import SessionLocal
from app.schemas.car import CarResponse, CarCreate, CarUpdate
from app.models.car import Car  # Assuming Car is the SQLAlchemy model for cars
from app.cruds.car import create_car, get_cars, get_car, update_car, delete_car  # CRUD methods

router = APIRouter()

# Get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def map_car_to_response(car: Car) -> CarResponse:
    """Map SQLAlchemy Car model to CarResponse schema."""
    garages = [
        {
            "id": garage.id,
            "name": garage.name,
            "location": garage.location,
            "city": garage.city,
            "capacity": garage.capacity,
        }
        for garage in car.garages
    ]
    return CarResponse(
        id=car.id,
        make=car.make,
        model=car.model,
        productionYear=car.production_year,
        licensePlate=car.license_plate,
        garages=garages,
    )


@router.post("/cars", response_model=CarResponse)
def create_car_endpoint(car: CarCreate, db: Session = Depends(get_db)):
    db_car = create_car(db=db, car=car)  # Call the create_car function from your CRUD module
    return map_car_to_response(db_car)


@router.get("/cars", response_model=List[CarResponse])
def list_cars_endpoint(
    carMake: Optional[str] = None,
    garageId: Optional[int] = None,
    fromYear: Optional[int] = None,
    toYear: Optional[int] = None,
    db: Session = Depends(get_db),
):
    cars = get_cars(db=db, make=carMake, garage_id=garageId, from_year=fromYear, to_year=toYear)
    return [map_car_to_response(car) for car in cars]


@router.get("/cars/{id}", response_model=CarResponse)
def get_car_endpoint(id: int, db: Session = Depends(get_db)):
    car = get_car(db=db, car_id=id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return map_car_to_response(car)


@router.put("/cars/{id}", response_model=CarResponse)
def update_car_endpoint(id: int, car: CarUpdate, db: Session = Depends(get_db)):
    updated_car = update_car(db=db, car_id=id, car=car)
    if not updated_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return map_car_to_response(updated_car)


@router.delete("/cars/{id}", response_model=dict)
def delete_car_endpoint(id: int, db: Session = Depends(get_db)):
    deleted_car = delete_car(db=db, car_id=id)
    if not deleted_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": f"Car with ID {id} deleted successfully"}

