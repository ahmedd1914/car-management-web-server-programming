from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.car_garage_association import car_garage_association
from app.models.database import Base


# Car Model
class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    production_year = Column(Integer)
    license_plate = Column(String, unique=True, index=True)

    # Many-to-Many relationship with garages
    garages = relationship("Garage", secondary=car_garage_association, back_populates="cars")

    # One-to-Many relationship with maintenance records
    maintenance_requests = relationship("MaintenanceRequest", back_populates="car")