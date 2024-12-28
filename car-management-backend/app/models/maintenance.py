from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.models.database import Base


class MaintenanceRequest(Base):
    """ Maintenance request model """
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    service_type = Column(String, nullable=False)
    scheduled_date = Column(Date, nullable=False)  # Changed from String to Date
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)

    # Relationships
    car = relationship("Car", back_populates="maintenance_requests")
    garage = relationship("Garage", back_populates="maintenance_requests")
