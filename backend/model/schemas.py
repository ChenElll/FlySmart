from pydantic import BaseModel

# ------- Plane-related Schemas ------- #
# These classes define how plane data is validated and structured
# when being sent to or returned from the API.

class PlaneBase(BaseModel):
    """Base schema with common plane attributes used for input/output."""
    Name: str
    Year: int
    MadeBy: str
    Picture: str | None = None
    NumOfSeats1: int
    NumOfSeats2: int
    NumOfSeats3: int


class PlaneCreate(PlaneBase):
    """Schema used when creating a new plane (inherits from PlaneBase)."""
    pass


class PlaneUpdate(PlaneBase):
    """Schema used when updating an existing plane (same fields as creation)."""
    pass


class PlaneRead(PlaneBase):
    """Schema used for reading plane data from the database (includes ID)."""
    PlaneId: int

    class Config:
        # This allows Pydantic to read data directly from ORM models (SQLAlchemy)
        from_attributes = True


class PlaneDeleteResponse(BaseModel):
    """Schema for a successful delete response, includes deleted plane info."""
    detail: str
    deleted_plane: PlaneRead
