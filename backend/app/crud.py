from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Flight
from schemas import FlightCreate

# ---------------- Flights CRUD ----------------

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

def delete_flight(db: Session, flight_id: int):
    flight = get_flight_by_id(db, flight_id)
    if flight:
        db.delete(flight)
        db.commit()
        return True
    return False

def update_flight(db: Session, flight_id: int, flight_data: FlightCreate):
    flight = get_flight_by_id(db, flight_id)
    if not flight:
        return None
    for key, value in flight_data.model_dump().items():
        setattr(flight, key, value)
    db.commit()
    db.refresh(flight)
    return flight