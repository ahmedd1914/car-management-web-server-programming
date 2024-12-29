from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.car import Car
from app.models.garage import Garage
from app.schemas.car import CarCreate, CarUpdate
from app.cruds.utils import get_or_404, update_relationship

from datetime import datetime


def create_car(db: Session, car):
    # Ensure the production year is valid
    if car.production_year > datetime.now().year:
        raise ValueError("Production year cannot be in the future.")

    # Exclude garage_ids when creating the Car instance
    car_data = car.dict(exclude={"garage_ids"})
    db_car = Car(**car_data)

    # Assign garages based on provided garage_ids
    if car.garage_ids:
        garages = db.query(Garage).filter(Garage.id.in_(car.garage_ids)).all()
        if len(garages) != len(car.garage_ids):
            raise ValueError("One or more garage IDs do not exist.")
        db_car.garages.extend(garages)  # Assuming a relationship like `garages = relationship("Garage")`

    # Save the car in the database
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

def get_car(db: Session, car_id: int):
    return get_or_404(db, Car, car_id, "Car not found")


def get_cars(db: Session, make: str = None, garage_id: int = None, from_year: int = None, to_year: int = None):
    query = db.query(Car)
    if make:
        query = query.filter(Car.make.ilike(f"%{make}%"))
    if garage_id:
        query = query.filter(Car.garages.any(Garage.id == garage_id))
    if from_year:
        query = query.filter(Car.production_year >= from_year)
    if to_year:
        query = query.filter(Car.production_year <= to_year)
    return query.all()


def update_car(db: Session, car_id: int, car: CarUpdate):
    db_car = get_or_404(db, Car, car_id, "Car not found")
    for key, value in car.dict(exclude={"garageIds"}, exclude_unset=True).items():
        setattr(db_car, key, value)
    if car.garage_ids:
        update_relationship(db, db_car, "garages", Garage, car.garage_ids)
    db.commit()
    db.refresh(db_car)
    return db_car


def delete_car(db: Session, car_id: int):
    db_car = get_or_404(db, Car, car_id, "Car not found")
    db.delete(db_car)
    db.commit()
    return db_car
