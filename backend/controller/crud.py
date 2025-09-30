from sqlalchemy.orm import Session
from backend.model.models import Plane
from backend.model.schemas import (
    PlaneCreate, PlaneUpdate
)
from fastapi import HTTPException


#----------plane CRUD Operations----------#

def get_all_planes(db: Session):
    return db.query(Plane).all()

def get_plane_by_id(db: Session, plane_id: int):
    return db.query(Plane).filter(Plane.PlaneId == plane_id).first()

def create_plane(db: Session, plane_data: PlaneCreate):
    new_plane = Plane(**plane_data.model_dump())
    db.add(new_plane)
    db.commit()
    db.refresh(new_plane)
    return new_plane

def update_plane(db: Session, plane_id: int, plane_data: PlaneUpdate):
    plane = get_plane_by_id(db, plane_id)
    if not plane:
        raise HTTPException(status_code=404, detail="Plane not found")
    for key, value in plane_data.model_dump().items():
        setattr(plane, key, value)
    db.commit()
    db.refresh(plane)
    return plane

def delete_plane(db: Session, plane_id: int):
    plane = get_plane_by_id(db, plane_id)
    if not plane:
        raise HTTPException(status_code=404, detail="Plane not found")
    
    deleted_plane_data = {
        "PlaneId": plane.PlaneId,
        "Name": plane.Name,
        "Year": plane.Year,
        "MadeBy": plane.MadeBy,
        "Picture": plane.Picture,
        "NumOfSeats1": plane.NumOfSeats1,
        "NumOfSeats2": plane.NumOfSeats2,
        "NumOfSeats3": plane.NumOfSeats3,
    }

    db.delete(plane)
    db.commit()
    
    return {
        "detail": "Plane deleted successfully",
        "deleted_plane": deleted_plane_data
    }
