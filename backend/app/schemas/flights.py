from pydantic import BaseModel
from datetime import datetime

class FlightRead(BaseModel):
    FlightId: int
    PlaneId: int
    DepartureLocation: str
    ArrivalLocation: str
    DepartureDateTime: datetime
    EstimatedArrivalDateTime: datetime

    class Config:
        from_attributes = True
