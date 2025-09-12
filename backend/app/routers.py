from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from db import get_db
import crud
from schemas import FlightCreate, FlightRead

router = APIRouter()

@router.get("/flights", response_model=list[FlightRead])
def get_all(db: Session = Depends(get_db)):
    return crud.get_all_flights(db)

@router.post("/flights", response_model=FlightRead)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    return crud.create_flight(db, flight)

@router.delete("/flights/{flight_id}")
def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    success = crud.delete_flight(db, flight_id)
    if not success:
        raise HTTPException(status_code=404, detail="Flight not found")
    return {"detail": "Flight deleted"}

@router.put("/flights/{flight_id}", response_model=FlightRead)
def update_flight(flight_id: int, flight: FlightCreate, db: Session = Depends(get_db)):
    updated = crud.update_flight(db, flight_id, flight)
    if not updated:
        raise HTTPException(status_code=404, detail="Flight not found")
    return updated
