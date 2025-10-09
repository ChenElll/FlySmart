# frontend/model/plane_entity.py
from dataclasses import dataclass
from typing import Optional, List
from .http import session, PLANES_URL, DEFAULT_TIMEOUT


@dataclass
class PlaneEntity:
    """
    Data model representing a single plane entity.
    Handles conversion to/from dicts and REST API communication.
    """
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
        """
        Creates a PlaneEntity instance from a dictionary (usually from API JSON).
        Handles both PlaneId and FlightId for flexibility.
        """
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
        """
        Converts this PlaneEntity instance to a dictionary
        suitable for sending as JSON in API requests.
        """
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
        """
        Fetches all planes from the API.
        Returns a list of PlaneEntity instances.
        """
        r = session.get(PLANES_URL, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return [PlaneEntity.from_dict(p) for p in r.json()]

    @staticmethod
    def get_by_id(plane_id: int) -> Optional["PlaneEntity"]:
        """
        Fetches a single plane by its ID from the API.
        Returns a PlaneEntity instance or None if not found.
        """
        r = session.get(f"{PLANES_URL}/{plane_id}", timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return PlaneEntity.from_dict(r.json())

    # ------------------------------------------------------------
    @staticmethod
    def create(data: dict) -> Optional["PlaneEntity"]:
        """
        Creates a new plane on the server using POST request.
        Returns a PlaneEntity representing the created object.
        """
        r = session.post(PLANES_URL, json=data, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        created = r.json()
        return PlaneEntity.from_dict(created)

    @staticmethod
    def update(plane_id: int, data: dict) -> Optional["PlaneEntity"]:
        """
        Updates an existing plane on the server using PUT request.
        Returns a PlaneEntity representing the updated object.
        """
        r = session.put(f"{PLANES_URL}/{plane_id}", json=data, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        updated = r.json()
        return PlaneEntity.from_dict(updated)

    @staticmethod
    def delete(plane_id: int) -> bool:
        """
        Deletes a plane by its ID using DELETE request.
        Returns True if deletion was successful.
        """
        r = session.delete(f"{PLANES_URL}/{plane_id}", timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return True
