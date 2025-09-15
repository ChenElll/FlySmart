from sqlalchemy.orm import Session
from model.models import Flight
from model.schemas import FlightCreate, FlightUpdate
from fastapi import HTTPException

def get_all_flights(db: Session):
    return db.query(Flight).all()

def get_flight_by_id(db: Session, flight_id: int):
    return db.query(Flight).filter(Flight.FlightId == flight_id).first()

def create_flight(db: Session, flight_data: FlightCreate):
    new_flight = Flight(**flight_data.model_dump())
    db.add(new_flight)
    db.commit()
    db.refresh(new_flight)
    return new_flight

def update_flight(db: Session, flight_id: int, flight_data: FlightUpdate):
    flight = get_flight_by_id(db, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    for key, value in flight_data.model_dump().items():
        setattr(flight, key, value)
    db.commit()
    db.refresh(flight)
    return flight

def delete_flight(db: Session, flight_id: int):
    flight = get_flight_by_id(db, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    db.delete(flight)
    db.commit()
    return {"detail": "Flight deleted successfully"}
