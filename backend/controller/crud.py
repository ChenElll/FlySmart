from sqlalchemy.orm import Session
from backend.model.models import Plane
from backend.model.schemas import PlaneCreate, PlaneUpdate
from fastapi import HTTPException


# ---------- Plane CRUD Operations ---------- #

def get_all_planes(db: Session):
    """Retrieve all planes from the database."""
    return db.query(Plane).all()


def get_plane_by_id(db: Session, plane_id: int):
    """Retrieve a specific plane by its unique ID."""
    return db.query(Plane).filter(Plane.PlaneId == plane_id).first()


def create_plane(db: Session, plane_data: PlaneCreate):
    """
    Create a new plane record in the database.
    - Accepts a validated Pydantic model (PlaneCreate)
    - Adds it to the database and commits
    - Returns the created Plane object
    """
    new_plane = Plane(**plane_data.model_dump())
    db.add(new_plane)
    db.commit()
    db.refresh(new_plane)
    return new_plane


def update_plane(db: Session, plane_id: int, plane_data: PlaneUpdate):
    """
    Update an existing plane record by ID.
    - Looks up the plane by ID
    - Updates only provided fields
    - Raises 404 error if the plane does not exist
    """
    plane = get_plane_by_id(db, plane_id)
    if not plane:
        raise HTTPException(status_code=404, detail="Plane not found")
    for key, value in plane_data.model_dump().items():
        setattr(plane, key, value)
    db.commit()
    db.refresh(plane)
    return plane


def delete_plane(db: Session, plane_id: int):
    """
    Delete a plane record by ID.
    - Validates existence of the plane
    - Deletes it from the database
    - Returns structured response with details
    """
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
