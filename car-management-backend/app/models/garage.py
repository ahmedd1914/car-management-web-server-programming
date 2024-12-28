from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.models.database import Base

from app.models.car_garage_association import car_garage_association


# Garage Model
class Garage(Base):
    __tablename__ = "garages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)
    city = Column(String)
    capacity = Column(Integer, default=0, nullable=False)

    # Many-to-Many relationship with cars
    cars = relationship("Car", secondary=car_garage_association, back_populates="garages")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="garage")