from .plane_view import PlaneView
from .plane_card import PlaneCard
from .plane_details_dialog import PlaneDetailsDialog
from .image_loader import ImageLoader  # 👈 שינוי כאן


__all__ = [
    "PlaneView",
    "PlaneCard",
    "PlaneDetailsDialog",
    "ImageLoader",  # 👈 במקום ImageCacheManager
]
