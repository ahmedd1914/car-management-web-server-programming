from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.cruds.utils import get_or_404
from app.models.garage import Garage
from app.schemas.garage import GarageCreate, GarageUpdate


def create_garage(db: Session, garage: GarageCreate):
    if garage.capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be positive.")
    db_garage = Garage(**garage.dict())
    db.add(db_garage)
    db.commit()
    db.refresh(db_garage)
    return db_garage


def get_garage(db: Session, garage_id: int):
    return get_or_404(db, Garage, garage_id, "Garage not found")


def get_garages(db: Session, city: str = None):
    query = db.query(Garage)
    if city:
        query = query.filter(Garage.city.ilike(f"%{city}%"))
    return query.all()


def update_garage(db: Session, garage_id: int, garage: GarageUpdate):
    db_garage = get_or_404(db, Garage, garage_id, "Garage not found")
    for key, value in garage.dict(exclude_unset=True).items():
        setattr(db_garage, key, value)
    db.commit()
    db.refresh(db_garage)
    return db_garage


def delete_garage(db: Session, garage_id: int):
    db_garage = get_or_404(db, Garage, garage_id, "Garage not found")
    db.delete(db_garage)
    db.commit()
    return db_garage
