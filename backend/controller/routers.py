from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.model.db import get_db
from backend.controller import crud
from backend.model.schemas import PlaneCreate, PlaneUpdate, PlaneRead, PlaneDeleteResponse
from typing import List


# ---------- Planes Router ---------- #
plane_router = APIRouter(prefix="/planes", tags=["Planes"])

@plane_router.get("/", response_model=List[PlaneRead])
def read_planes(db: Session = Depends(get_db)):
    return crud.get_all_planes(db)

@plane_router.get("/{plane_id}", response_model=PlaneRead)
def read_plane(plane_id: int, db: Session = Depends(get_db)):
    return crud.get_plane_by_id(db, plane_id)

@plane_router.post("/", response_model=PlaneRead)
def create_plane(plane: PlaneCreate, db: Session = Depends(get_db)):
    return crud.create_plane(db, plane)

@plane_router.put("/{plane_id}", response_model=PlaneRead)
def update_plane(plane_id: int, plane: PlaneUpdate, db: Session = Depends(get_db)):
    return crud.update_plane(db, plane_id, plane)


@plane_router.delete("/{plane_id}", response_model=PlaneDeleteResponse)
def delete_plane(plane_id: int, db: Session = Depends(get_db)):
    return crud.delete_plane(db, plane_id)