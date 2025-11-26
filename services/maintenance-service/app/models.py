from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class MaintenanceTypeEnum(str, enum.Enum):
    preventive = "preventive"
    corrective = "corrective"

class MaintenanceStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class MaintenanceType(Base):
    __tablename__ = "maintenance_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, nullable=False, index=True)
    maintenance_type_id = Column(Integer, ForeignKey("maintenance_types.id"))
    type = Column(Enum(MaintenanceTypeEnum), nullable=False)
    scheduled_date = Column(Date)
    performed_date = Column(Date, index=True)
    technician = Column(String(100))
    provider_id = Column(Integer)
    description = Column(Text, nullable=False)
    diagnosis = Column(Text)
    solution = Column(Text)
    cost = Column(Numeric(10, 2))
    status = Column(Enum(MaintenanceStatusEnum), default=MaintenanceStatusEnum.scheduled, index=True)
    next_maintenance_date = Column(Date)
    attachments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)

    maintenance_type = relationship("MaintenanceType")

class MaintenancePart(Base):
    __tablename__ = "maintenance_parts"

    id = Column(Integer, primary_key=True, index=True)
    maintenance_id = Column(Integer, ForeignKey("maintenance.id"), nullable=False)
    part_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

    maintenance = relationship("Maintenance", backref="parts")
