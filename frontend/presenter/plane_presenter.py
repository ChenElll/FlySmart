import requests
from frontend.model.plane_entity import PlaneEntity
import time
import requests

API_BASE = "http://127.0.0.1:8000"
PLANES_URL = f"{API_BASE}/planes"

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
    def __init__(self, view):
        self.view = view

    def load_planes(self):
        # Wait until backend is alive
        if not wait_for_backend():
            self.view.show_error("Backend server is not responding. Please start it.")
            return

        try:
            response = requests.get(PLANES_URL)
            response.raise_for_status()
            planes = [PlaneEntity(**p) for p in response.json()]
            self.view.show_planes(planes)
        except Exception as e:
            self.view.show_error(f"Error loading planes: {e}")
