import time
from frontend.model.plane_entity import PlaneEntity
import requests

API_BASE = "http://127.0.0.1:8000"

def wait_for_backend(timeout: int = 60, interval: int = 3):
    """
    Wait until the backend is available or timeout is reached.
    """
    start = time.time()
    while True:
        try:
            response = requests.get(f"{API_BASE}/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is available!")
                return True
        except requests.exceptions.RequestException:
            print("⏳ Waiting for backend to start...")

        if time.time() - start > timeout:
            print("❌ Backend did not start in time.")
            return False

        time.sleep(interval)


class PlanePresenter:
    """
    Acts as the middle layer between the View (PlaneView) and the Model (PlaneEntity).
    Responsible for all CRUD logic and data flow.
    """
    def __init__(self, view):
        self.view = view

    # ------------------- READ -------------------
    def load_planes(self):
        """Fetch and display all planes."""
        if not wait_for_backend():
            self.view.show_error("Backend server is not responding. Please start it.")
            return

        planes = PlaneEntity.get_all()
        if not planes:
            self.view.show_error("No planes found or failed to load.")
            return

        self.view.show_planes(planes)

    def show_plane_details(self, plane_id: int):
        """Display details of a selected plane."""
        plane = PlaneEntity.get_by_id(plane_id)
        if plane:
            self.view.show_plane_details(plane)
        else:
            self.view.show_error(f"Plane ID {plane_id} not found.")

    # ------------------- CREATE -------------------
    def add_plane(self, name, year, made_by, picture, seats1, seats2, seats3):
        """Add a new plane."""
        try:
            new_plane = PlaneEntity(
                PlaneId=0,
                Name=name,
                Year=year,
                MadeBy=made_by,
                Picture=picture,
                NumOfSeats1=seats1,
                NumOfSeats2=seats2,
                NumOfSeats3=seats3,
            )
            if new_plane.create():
                self.load_planes()
            else:
                self.view.show_error("Failed to add new plane.")
        except Exception as e:
            self.view.show_error(f"Error adding plane: {e}")

    # ------------------- UPDATE -------------------
    def update_plane(self, plane_id, name, year, made_by, picture, seats1, seats2, seats3):
        """Update an existing plane."""
        plane = PlaneEntity(
            PlaneId=plane_id,
            Name=name,
            Year=year,
            MadeBy=made_by,
            Picture=picture,
            NumOfSeats1=seats1,
            NumOfSeats2=seats2,
            NumOfSeats3=seats3,
        )
        try:
            if plane.update():
                self.load_planes()
            else:
                self.view.show_error(f"Failed to update plane {plane_id}.")
        except Exception as e:
            self.view.show_error(f"Error updating plane: {e}")

    # ------------------- DELETE -------------------
    def delete_plane(self, plane_id):
        """Delete a plane by ID."""
        plane = PlaneEntity.get_by_id(plane_id)
        if not plane:
            self.view.show_error(f"Plane ID {plane_id} not found.")
            return

        try:
            if plane.delete():
                print(f"✅ Plane {plane_id} deleted successfully.")
                self.load_planes()
            else:
                self.view.show_error(f"Failed to delete plane {plane_id}.")
        except Exception as e:
            self.view.show_error(f"Error deleting plane: {e}")
