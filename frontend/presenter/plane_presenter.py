from PySide6.QtWidgets import QMessageBox
from ..model.plane_entity import PlaneEntity
from ..view.plane_form_dialog import PlaneFormDialog


class PlanePresenter:
    """Presenter layer that connects the View and Model — manages all CRUD operations for planes."""

    def __init__(self, view):
        self.view = view  # Reference to the View layer (plane_view)

    # ------------------------------------------------------------
    def load_planes(self):
        """Fetches all planes from the server and displays them in the view."""
        try:
            planes = PlaneEntity.get_all()
            self.view.show_planes(planes)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load planes:\n{e}")

    # ------------------------------------------------------------
    def add_plane(self, data: dict):
        """Creates a new plane record and displays it in the view."""
        try:
            plane = PlaneEntity(**data)      # Create PlaneEntity instance from the input data
            plane.create(data)               # Send POST request to backend
            self.view.add_plane_card(plane)  # Add the new card visually
            return True, ""
        except Exception as e:
            return False, f"Error adding plane: {e}"

    # ------------------------------------------------------------
    def update_plane(self, plane_id: int, data: dict):
        """Updates an existing plane's data both in the backend and the view."""
        try:
            plane = PlaneEntity.update(plane_id, data)
            if plane:
                # Refresh the updated card visually, if supported by the view
                if hasattr(self.view, "refresh_plane_card"):
                    self.view.refresh_plane_card(plane)
                return True, ""
            return False, "Failed to update plane."
        except Exception as e:
            return False, f"Error updating plane: {e}"

    # ------------------------------------------------------------
    def delete_plane(self, plane_id: int):
        """Deletes a plane from both backend and the view."""
        try:
            plane = PlaneEntity.get_by_id(plane_id)
            if not plane:
                return False, "Plane not found."

            plane.delete(plane_id)  # Request deletion from backend

            # Remove the card from the visual view if supported
            if hasattr(self.view, "remove_plane_card"):
                self.view.remove_plane_card(plane_id)

            return True, "Plane deleted successfully."
        except Exception as e:
            return False, f"Error deleting plane: {e}"

    # ------------------------------------------------------------
    def save_plane(self, mode: str, data: dict, plane=None):
        """Saves or updates a plane depending on the given mode (add/edit)."""
        try:
            if mode == "add":
                return self.add_plane(data)
            elif mode == "edit" and plane:
                return self.update_plane(plane.PlaneId, data)
            else:
                return False, "Invalid save mode."
        except Exception as e:
            return False, f"Unexpected error while saving: {e}"

    # ------------------------------------------------------------
    def open_add_plane(self):
        """Opens a dialog for adding a new plane and reloads data after successful save."""
        try:
            dialog = PlaneFormDialog(self, mode="add")
            if dialog.exec():
                self.load_planes()  # Refresh view after adding
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to open Add Plane dialog:\n{e}")

    # ------------------------------------------------------------
    def open_edit_plane(self, plane):
        """Opens a dialog for editing an existing plane and reloads data after update."""
        try:
            dialog = PlaneFormDialog(self, mode="edit", plane=plane)
            if dialog.exec():
                self.load_planes()  # Refresh view after update
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to open Edit Plane dialog:\n{e}")

    # ------------------------------------------------------------
    def get_plane_by_id(self, plane_id: int):
        """Fetches a specific plane by ID for refreshing the details view."""
        try:
            return PlaneEntity.get_by_id(plane_id)
        except Exception:
            return None

    # ------------------------------------------------------------
    def get_displayed_planes(self):
        """
        Returns the list of currently displayed (filtered) planes in the view.
        Filters by search text, manufacturer, and year based on user input.
        """
        if hasattr(self.view, "planes"):
            search_text = self.view.search_input.text().strip().lower()
            maker = self.view.made_by_combo.currentText()
            year = self.view.year_combo.currentText()

            filtered = []
            for p in self.view.planes:
                match_name = (
                    search_text in p.Name.lower() or search_text in p.MadeBy.lower()
                )
                match_maker = maker == "All Manufacturers" or p.MadeBy == maker
                match_year = year == "All Years" or str(p.Year) == year
                if match_name and match_maker and match_year:
                    filtered.append(p)
            return filtered
        return []
