from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime

from app.models.database import Base

car_garage_association = Table(
    "car_garage_association",
    Base.metadata,
    Column("car_id", Integer, ForeignKey("cars.id"), primary_key=True),
    Column("garage_id", Integer, ForeignKey("garages.id"), primary_key=True),
)