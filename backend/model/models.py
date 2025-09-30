from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ------- Plane Model ------- #
class Plane(Base):
    __tablename__ = "Planes"

    PlaneId = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
    Year = Column(Integer, nullable=False)
    MadeBy = Column(String, nullable=False)
    Picture = Column(String, nullable=True)
    NumOfSeats1 = Column(Integer, nullable=False)
    NumOfSeats2 = Column(Integer, nullable=False)
    NumOfSeats3 = Column(Integer, nullable=False)
