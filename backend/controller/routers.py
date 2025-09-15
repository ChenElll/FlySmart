from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from model.db import get_db
from controller import crud
from model.schemas import FlightCreate, FlightUpdate, FlightRead
from typing import List

router = APIRouter(prefix="/flights", tags=["Flights"])

@router.get("/", response_model=List[FlightRead])
def read_flights(db: Session = Depends(get_db)):
    return crud.get_all_flights(db)

@router.get("/{flight_id}", response_model=FlightRead)
def read_flight(flight_id: int, db: Session = Depends(get_db)):
    return crud.get_flight_by_id(db, flight_id)

@router.post("/", response_model=FlightRead)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    return crud.create_flight(db, flight)

@router.put("/{flight_id}", response_model=FlightRead)
def update_flight(flight_id: int, flight: FlightUpdate, db: Session = Depends(get_db)):
    return crud.update_flight(db, flight_id, flight)

@router.delete("/{flight_id}")
def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    return crud.delete_flight(db, flight_id)
