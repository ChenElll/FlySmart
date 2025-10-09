from PySide6.QtWidgets import QMessageBox
from ..model.plane_entity import PlaneEntity
from ..view.plane_form_dialog import PlaneFormDialog
from ..model.plane_entity import PlaneEntity



class PlanePresenter:
    """שכבת ביניים בין ה־View למודל — מנהלת CRUD למטוסים"""

    def __init__(self, view):
        self.view = view

    # ------------------------------------------------------------
    def load_planes(self):
        """טוען את רשימת המטוסים מהשרת"""
        try:
            planes = PlaneEntity.get_all()
            self.view.show_planes(planes)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load planes:\n{e}")

    # ------------------------------------------------------------
    def add_plane(self, data: dict):
        """הוספת מטוס חדש"""
        try:
            plane = PlaneEntity(**data)  # יוצרים מופע חדש
            plane.create(data)               # שולחים לשרת
            self.view.add_plane_card(plane)
            return True, ""
        except Exception as e:
            return False, f"Error adding plane: {e}"

    # ------------------------------------------------------------
    def update_plane(self, plane_id: int, data: dict):
        """עדכון נתוני מטוס קיים"""
        try:
            plane = PlaneEntity.update(plane_id, data)
            if plane:
                if hasattr(self.view, "refresh_plane_card"):
                    self.view.refresh_plane_card(plane)
                return True, ""
            return False, "Failed to update plane."
        except Exception as e:
            return False, f"Error updating plane: {e}"


    # ------------------------------------------------------------
    def delete_plane(self, plane_id: int):
        """מחיקת מטוס לפי מזהה"""
        try:
            plane = PlaneEntity.get_by_id(plane_id)
            if not plane:
                return False, "Plane not found."

            plane.delete(plane_id)

            if hasattr(self.view, "remove_plane_card"):
                self.view.remove_plane_card(plane_id)

            return True, "Plane deleted successfully."
        except Exception as e:
            return False, f"Error deleting plane: {e}"

    # ------------------------------------------------------------
    def save_plane(self, mode: str, data: dict, plane=None):
        """שומר או מעדכן מטוס בהתאם למצב"""
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
        """פותח חלון להוספת מטוס חדש"""
        try:
            dialog = PlaneFormDialog(self, mode="add")
            if dialog.exec():
                self.load_planes()  # רענון לאחר שמירה
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to open Add Plane dialog:\n{e}")

    # ------------------------------------------------------------
    def open_edit_plane(self, plane):
        """פותח חלון עריכה של מטוס קיים"""
        try:
            dialog = PlaneFormDialog(self, mode="edit", plane=plane)
            if dialog.exec():
                self.load_planes()  # רענון לאחר עדכון
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to open Edit Plane dialog:\n{e}")

    # ------------------------------------------------------------
    def get_plane_by_id(self, plane_id: int):
        """מביא מטוס ספציפי מהשרת לרענון"""
        try:
            return PlaneEntity.get_by_id(plane_id)
        except Exception:
            return None
