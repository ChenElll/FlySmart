from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.model.db import get_db
from backend.controller import crud
from backend.model.schemas import PlaneCreate, PlaneUpdate, PlaneRead, PlaneDeleteResponse
from typing import List


# ============================================================
# 🛫 Planes Router — defines all API endpoints for plane data
# ============================================================

# The router groups all /planes-related routes under one prefix
plane_router = APIRouter(prefix="/planes", tags=["Planes"])


# ------------------------------------------------------------
# GET /planes — Retrieve all planes
# ------------------------------------------------------------
@plane_router.get("/", response_model=List[PlaneRead])
def read_planes(db: Session = Depends(get_db)):
    """
    Fetch all planes from the database.
    - Uses a SQLAlchemy session provided by `get_db`.
    - Calls the CRUD layer to handle the query logic.
    """
    return crud.get_all_planes(db)


# ------------------------------------------------------------
# GET /planes/{plane_id} — Retrieve a single plane by ID
# ------------------------------------------------------------
@plane_router.get("/{plane_id}", response_model=PlaneRead)
def read_plane(plane_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single plane based on its unique ID.
    Returns a PlaneRead schema object or raises an error if not found.
    """
    return crud.get_plane_by_id(db, plane_id)


# ------------------------------------------------------------
# POST /planes — Create a new plane
# ------------------------------------------------------------
@plane_router.post("/", response_model=PlaneRead)
def create_plane(plane: PlaneCreate, db: Session = Depends(get_db)):
    """
    Add a new plane to the database.
    - Validates request body using PlaneCreate schema.
    - Returns the created plane data.
    """
    return crud.create_plane(db, plane)


# ------------------------------------------------------------
# PUT /planes/{plane_id} — Update existing plane
# ------------------------------------------------------------
@plane_router.put("/{plane_id}", response_model=PlaneRead)
def update_plane(plane_id: int, plane: PlaneUpdate, db: Session = Depends(get_db)):
    """
    Update plane details based on the provided plane ID.
    - Accepts PlaneUpdate schema for partial or full update.
    - Returns the updated plane data.
    """
    return crud.update_plane(db, plane_id, plane)


# ------------------------------------------------------------
# DELETE /planes/{plane_id} — Delete a plane
# ------------------------------------------------------------
@plane_router.delete("/{plane_id}", response_model=PlaneDeleteResponse)
def delete_plane(plane_id: int, db: Session = Depends(get_db)):
    """
    Delete a plane from the database by its ID.
    - Returns a message confirming the deletion.
    """
    return crud.delete_plane(db, plane_id)
