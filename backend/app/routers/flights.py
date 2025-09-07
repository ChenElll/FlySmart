from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.flights import Flight
from app.schemas.flights import FlightRead
from sqlalchemy import select

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/", response_model=list[FlightRead])
def get_all_flights(db: Session = Depends(get_db)):
    stmt = select(Flight)
    result = db.execute(stmt).scalars().all()
    return result
