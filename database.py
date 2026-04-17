from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database file
DATABASE_URL = "sqlite:///./watchman.db"

# Create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session
SessionLocal = sessionmaker(bind=engine)

# Base class
Base = declarative_base()


# 👤 Resident Table
class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    flat_number = Column(String)
    vehicle_number = Column(String, unique=True)
    
from datetime import datetime
from sqlalchemy import Boolean, DateTime

class GuestEntry(Base):
    __tablename__ = "guest_entries"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String)
    vehicle_plate = Column(String)
    flat_no = Column(String)
    purpose = Column(String)

    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)