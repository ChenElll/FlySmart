# frontend/model/plane_entity.py
from dataclasses import dataclass
from typing import Optional, List
from .http import session, PLANES_URL, DEFAULT_TIMEOUT

@dataclass
class PlaneEntity:
    PlaneId: int
    Name: str
    Year: int
    MadeBy: str
    Picture: Optional[str]
    NumOfSeats1: int
    NumOfSeats2: int
    NumOfSeats3: int

    @classmethod
    def from_dict(cls, d: dict):
        pid = d.get("PlaneId")
        # אם ה־API הישן מחזיר FlightId — עדיף לתקן בשרת; בינתיים:
        if pid is None and "FlightId" in d:
            pid = d["FlightId"]
        return cls(
            PlaneId=int(pid),
            Name=str(d.get("Name", "")),
            Year=int(d.get("Year", 0)),
            MadeBy=str(d.get("MadeBy", "")),
            Picture=d.get("Picture") or None,
            NumOfSeats1=int(d.get("NumOfSeats1", 0)),
            NumOfSeats2=int(d.get("NumOfSeats2", 0)),
            NumOfSeats3=int(d.get("NumOfSeats3", 0)),
        )

    def to_dict(self, include_id=True):
        data = {
            "Name": self.Name,
            "Year": self.Year,
            "MadeBy": self.MadeBy,
            "Picture": self.Picture,
            "NumOfSeats1": self.NumOfSeats1,
            "NumOfSeats2": self.NumOfSeats2,
            "NumOfSeats3": self.NumOfSeats3,
        }
        if include_id:
            data["PlaneId"] = self.PlaneId
        return data

    @staticmethod
    def get_all() -> List["PlaneEntity"]:
        r = session.get(PLANES_URL, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return [PlaneEntity.from_dict(p) for p in r.json()]

    @staticmethod
    def get_by_id(plane_id: int) -> Optional["PlaneEntity"]:
        r = session.get(f"{PLANES_URL}/{plane_id}", timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return PlaneEntity.from_dict(r.json())

    def create(self) -> bool:
        # אל תשלחי PlaneId ביצירה
        r = session.post(PLANES_URL, json=self.to_dict(include_id=False), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        created = r.json()
        if isinstance(created, dict) and created.get("PlaneId"):
            self.PlaneId = int(created["PlaneId"])
        return True

    def update(self) -> bool:
        r = session.put(f"{PLANES_URL}/{self.PlaneId}", json=self.to_dict(), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return True

    def delete(self) -> bool:
        r = session.delete(f"{PLANES_URL}/{self.PlaneId}", timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return True
