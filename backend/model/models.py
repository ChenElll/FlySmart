from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Base class for all ORM models (each table in the DB will inherit from this)
Base = declarative_base()

# ------- Plane Model ------- #
class Plane(Base):
    """ORM model representing the 'Planes' table in the database."""
    
    __tablename__ = "Planes"  # The name of the table in SQL Server

    # --- Table Columns ---
    PlaneId = Column(Integer, primary_key=True, index=True)  # Unique identifier for each plane
    Name = Column(String, nullable=False)                    # Plane name (required)
    Year = Column(Integer, nullable=False)                   # Year of manufacture
    MadeBy = Column(String, nullable=False)                   # Manufacturer (e.g., Boeing, Airbus)
    Picture = Column(String, nullable=True)                   # Optional image URL or file path
    NumOfSeats1 = Column(Integer, nullable=False)             # Number of seats in first class
    NumOfSeats2 = Column(Integer, nullable=False)             # Number of seats in business class
    NumOfSeats3 = Column(Integer, nullable=False)             # Number of seats in economy class
