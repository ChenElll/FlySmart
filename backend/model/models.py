from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Flight(Base):
    __tablename__ = "Flights"

    FlightId = Column(Integer, primary_key=True, index=True)
    PlaneId = Column(Integer, nullable=False)
    DepartureLocation = Column(String, nullable=False)
    ArrivalLocation = Column(String, nullable=False)
    DepartureDateTime = Column(DateTime, nullable=False)
    EstimatedArrivalDateTime = Column(DateTime, nullable=False)
