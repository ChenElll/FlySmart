from dataclasses import dataclass

@dataclass
class PlaneEntity:
    PlaneId: int
    Name: str
    Year: int
    MadeBy: str
    Picture: str | None
    NumOfSeats1: int
    NumOfSeats2: int
    NumOfSeats3: int
