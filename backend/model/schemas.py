from pydantic import BaseModel
from datetime import datetime

class FlightBase(BaseModel):
    PlaneId: int
    DepartureLocation: str
    ArrivalLocation: str
    DepartureDateTime: datetime
    EstimatedArrivalDateTime: datetime

class FlightCreate(FlightBase):
    pass

class FlightUpdate(FlightBase):
    pass

class FlightRead(FlightBase):
    FlightId: int

    class Config:
        from_attributes = True
