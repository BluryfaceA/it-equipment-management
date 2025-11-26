from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, DateTime, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class EquipmentStatus(str, enum.Enum):
    operational = "operational"
    in_maintenance = "in_maintenance"
    broken = "broken"
    retired = "retired"
    in_storage = "in_storage"

class EquipmentCategory(Base):
    __tablename__ = "equipment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    building = Column(String(100), nullable=False)
    floor = Column(String(50))
    room = Column(String(50))
    department = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, nullable=False, index=True)
    serial_number = Column(String(100), index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("equipment_categories.id"))
    brand = Column(String(100))
    model = Column(String(100))
    purchase_date = Column(Date)
    purchase_price = Column(Numeric(12, 2))
    provider_id = Column(Integer)
    warranty_months = Column(Integer, default=12)
    warranty_end_date = Column(Date)
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.operational)
    current_location_id = Column(Integer, ForeignKey("locations.id"))
    assigned_to = Column(String(100))
    specifications = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)

    category = relationship("EquipmentCategory")
    location = relationship("Location")

class EquipmentLocationHistory(Base):
    __tablename__ = "equipment_location_history"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    assigned_to = Column(String(100))
    move_date = Column(Date, nullable=False)
    reason = Column(Text)
    moved_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment")
    location = relationship("Location")
