from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

os.makedirs("data", exist_ok=True)
DB_URL = "sqlite:///data/hospital.db"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class SensorRecord(Base):
    __tablename__ = "sensor_records"
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    metric = Column(String, index=True)
    value = Column(Float)
    unit = Column(String)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

class AlertRecord(Base):
    __tablename__ = "alert_records"
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    severity = Column(String)  # INFO/WARN/ALERT
    message = Column(String)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
