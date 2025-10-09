# frontend/model/plane_entity.py
from dataclasses import dataclass
from typing import Optional, List
from .http import session, PLANES_URL, DEFAULT_TIMEOUT


@dataclass
class PlaneEntity:
    PlaneId: Optional[int] = None
    Name: str = ""
    Year: int = 0
    MadeBy: str = ""
    Picture: Optional[str] = None
    NumOfSeats1: int = 0
    NumOfSeats2: int = 0
    NumOfSeats3: int = 0

    # ------------------------------------------------------------
    @classmethod
    def from_dict(cls, d: dict):
        pid = d.get("PlaneId") or d.get("FlightId")
        return cls(
            PlaneId=int(pid) if pid else None,
            Name=str(d.get("Name", "")),
            Year=int(d.get("Year", 0)),
            MadeBy=str(d.get("MadeBy", "")),
            Picture=d.get("Picture") or None,
            NumOfSeats1=int(d.get("NumOfSeats1", 0)),
            NumOfSeats2=int(d.get("NumOfSeats2", 0)),
            NumOfSeats3=int(d.get("NumOfSeats3", 0)),
        )

    # ------------------------------------------------------------
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
        if include_id and self.PlaneId:
            data["PlaneId"] = self.PlaneId
        return data

    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    @staticmethod
    def create(data: dict) -> Optional["PlaneEntity"]:
        """יוצר מטוס חדש בשרת ומחזיר מופע PlaneEntity"""
        r = session.post(PLANES_URL, json=data, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        created = r.json()
        return PlaneEntity.from_dict(created)


    @staticmethod
    def update(plane_id: int, data: dict) -> Optional["PlaneEntity"]:
        """מעדכן מטוס קיים"""
        r = session.put(f"{PLANES_URL}/{plane_id}", json=data, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        updated = r.json()
        return PlaneEntity.from_dict(updated)

    @staticmethod
    def delete(plane_id: int) -> bool:
        """מוחק מטוס לפי מזהה"""
        r = session.delete(f"{PLANES_URL}/{plane_id}", timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return True

