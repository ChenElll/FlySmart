from dataclasses import dataclass
import requests

API_BASE_URL = "http://127.0.0.1:8000/planes"

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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            PlaneId=data.get("FlightId") or data.get("PlaneId"),
            Name=data.get("Name"),
            Year=data.get("Year"),
            MadeBy=data.get("MadeBy"),
            Picture=data.get("Picture"),
            NumOfSeats1=data.get("NumOfSeats1"),
            NumOfSeats2=data.get("NumOfSeats2"),
            NumOfSeats3=data.get("NumOfSeats3"),
        )

    def to_dict(self):
        return {
            "PlaneId": self.PlaneId,
            "Name": self.Name,
            "Year": self.Year,
            "MadeBy": self.MadeBy,
            "Picture": self.Picture,
            "NumOfSeats1": self.NumOfSeats1,
            "NumOfSeats2": self.NumOfSeats2,
            "NumOfSeats3": self.NumOfSeats3,
        }

    # ---------- API Methods ----------
    @staticmethod
    def get_all():
        """Fetch all planes from backend"""
        try:
            res = requests.get(API_BASE_URL)
            res.raise_for_status()
            return [PlaneEntity.from_dict(p) for p in res.json()]
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch planes: {e}")
            return []

    @staticmethod
    def get_by_id(plane_id: int):
        try:
            res = requests.get(f"{API_BASE_URL}/{plane_id}")
            res.raise_for_status()
            return PlaneEntity.from_dict(res.json())
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch plane {plane_id}: {e}")
            return None

    def create(self):
        """Send POST request to create plane"""
        try:
            res = requests.post(API_BASE_URL, json=self.to_dict())
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to create plane: {e}")
            return False

    def update(self):
        try:
            res = requests.put(f"{API_BASE_URL}/{self.PlaneId}", json=self.to_dict())
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to update plane {self.PlaneId}: {e}")
            return False

    def delete(self):
        try:
            res = requests.delete(f"{API_BASE_URL}/{self.PlaneId}")
            res.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to delete plane {self.PlaneId}: {e}")
            return False
