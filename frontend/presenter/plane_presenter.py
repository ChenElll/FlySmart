import requests
from frontend.model.plane_entity import PlaneEntity

API_URL = "http://127.0.0.1:8000/planes"

class PlanePresenter:
    def __init__(self, view):
        self.view = view

    def load_planes(self):
        response = requests.get(API_URL)
        if response.status_code == 200:
            planes = [PlaneEntity(**p) for p in response.json()]
            self.view.show_planes(planes)
        else:
            self.view.show_error("Failed to load planes")
