from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Flight(Base):
    __tablename__ = "Flights"

    FlightId = Column(Integer, primary_key=True, index=True)
    PlaneId = Column(Integer)
    DepartureLocation = Column(String)
    ArrivalLocation = Column(String)
    DepartureDateTime = Column(DateTime)
    EstimatedArrivalDateTime = Column(DateTime)
