from pydantic import BaseModel


# ------- plane-related Schemas ------- #
class PlaneBase(BaseModel):
    Name: str
    Year: int
    MadeBy: str
    Picture: str | None = None
    NumOfSeats1: int
    NumOfSeats2: int
    NumOfSeats3: int


class PlaneCreate(PlaneBase):
    pass


class PlaneUpdate(PlaneBase):
    pass


class PlaneRead(PlaneBase):
    PlaneId: int

    class Config:
        from_attributes = True


class PlaneDeleteResponse(BaseModel):
    detail: str
    deleted_plane: PlaneRead
