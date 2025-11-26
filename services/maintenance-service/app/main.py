from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal
import time
from .database import get_db, engine, Base
from .models import Maintenance, MaintenanceType, MaintenancePart, MaintenanceTypeEnum, MaintenanceStatusEnum

app = FastAPI(title="Maintenance Service", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize database with retry logic"""
    max_retries = 30
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print(f"✅ Database connection established on attempt {attempt + 1}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Database connection attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SCHEMAS
# ============================================

class MaintenanceTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None

class MaintenanceTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

class MaintenancePartCreate(BaseModel):
    part_name: str
    quantity: int = 1
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None

class MaintenancePartResponse(BaseModel):
    id: int
    part_name: str
    quantity: int
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]

    class Config:
        from_attributes = True

class MaintenanceCreate(BaseModel):
    equipment_id: int
    maintenance_type_id: Optional[int] = None
    type: MaintenanceTypeEnum
    scheduled_date: Optional[date] = None
    performed_date: Optional[date] = None
    technician: Optional[str] = None
    provider_id: Optional[int] = None
    description: str
    diagnosis: Optional[str] = None
    solution: Optional[str] = None
    cost: Optional[Decimal] = None
    next_maintenance_date: Optional[date] = None
    parts: Optional[List[MaintenancePartCreate]] = []
    created_by: Optional[int] = None

class MaintenanceUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    performed_date: Optional[date] = None
    technician: Optional[str] = None
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    solution: Optional[str] = None
    cost: Optional[Decimal] = None
    status: Optional[MaintenanceStatusEnum] = None
    next_maintenance_date: Optional[date] = None

class MaintenanceResponse(BaseModel):
    id: int
    equipment_id: int
    type: str
    scheduled_date: Optional[date]
    performed_date: Optional[date]
    technician: Optional[str]
    provider_id: Optional[int]
    description: str
    diagnosis: Optional[str]
    solution: Optional[str]
    cost: Optional[Decimal]
    status: str
    next_maintenance_date: Optional[date]
    maintenance_type: Optional[MaintenanceTypeResponse]
    parts: List[MaintenancePartResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

# ============================================
# ENDPOINTS - MAINTENANCE TYPES
# ============================================

@app.get("/")
def read_root():
    return {"service": "Maintenance Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/types", response_model=MaintenanceTypeResponse)
def create_maintenance_type(
    maintenance_type: MaintenanceTypeCreate,
    db: Session = Depends(get_db)
):
    db_type = MaintenanceType(**maintenance_type.model_dump())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

@app.get("/types", response_model=List[MaintenanceTypeResponse])
def get_maintenance_types(db: Session = Depends(get_db)):
    types = db.query(MaintenanceType).all()
    return types

# ============================================
# ENDPOINTS - MAINTENANCE
# ============================================

@app.post("/maintenance", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(maintenance: MaintenanceCreate, db: Session = Depends(get_db)):
    # Crear mantenimiento
    parts_data = maintenance.parts
    maintenance_dict = maintenance.model_dump(exclude={'parts'})
    db_maintenance = Maintenance(**maintenance_dict)

    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)

    # Agregar partes si existen
    if parts_data:
        for part in parts_data:
            db_part = MaintenancePart(
                maintenance_id=db_maintenance.id,
                **part.model_dump()
            )
            db.add(db_part)
        db.commit()
        db.refresh(db_maintenance)

    return db_maintenance

@app.get("/maintenance", response_model=List[MaintenanceResponse])
def get_maintenance_records(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    type: Optional[MaintenanceTypeEnum] = None,
    status: Optional[MaintenanceStatusEnum] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Maintenance)

    if equipment_id:
        query = query.filter(Maintenance.equipment_id == equipment_id)
    if type:
        query = query.filter(Maintenance.type == type)
    if status:
        query = query.filter(Maintenance.status == status)
    if from_date:
        query = query.filter(Maintenance.performed_date >= from_date)
    if to_date:
        query = query.filter(Maintenance.performed_date <= to_date)

    maintenance_list = query.order_by(Maintenance.scheduled_date.desc())\
        .offset(skip).limit(limit).all()
    return maintenance_list

@app.get("/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return maintenance

@app.put("/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(
    maintenance_id: int,
    maintenance_update: MaintenanceUpdate,
    db: Session = Depends(get_db)
):
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    update_data = maintenance_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(maintenance, field, value)

    db.commit()
    db.refresh(maintenance)
    return maintenance

@app.delete("/maintenance/{maintenance_id}")
def delete_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    db.delete(maintenance)
    db.commit()
    return {"message": "Maintenance record deleted successfully"}

@app.get("/equipment/{equipment_id}/maintenance-history", response_model=List[MaintenanceResponse])
def get_equipment_maintenance_history(equipment_id: int, db: Session = Depends(get_db)):
    """Obtener historial completo de mantenimiento de un equipo"""
    history = db.query(Maintenance)\
        .filter(Maintenance.equipment_id == equipment_id)\
        .order_by(Maintenance.performed_date.desc())\
        .all()
    return history

@app.get("/equipment/{equipment_id}/next-maintenance")
def get_next_maintenance(equipment_id: int, db: Session = Depends(get_db)):
    """Obtener próximo mantenimiento programado de un equipo"""
    next_maintenance = db.query(Maintenance)\
        .filter(
            Maintenance.equipment_id == equipment_id,
            Maintenance.status == MaintenanceStatusEnum.scheduled,
            Maintenance.scheduled_date >= datetime.now().date()
        )\
        .order_by(Maintenance.scheduled_date.asc())\
        .first()

    if not next_maintenance:
        return {"message": "No upcoming maintenance scheduled"}

    return next_maintenance

@app.get("/upcoming-maintenance", response_model=List[MaintenanceResponse])
def get_upcoming_maintenance(days: int = 30, db: Session = Depends(get_db)):
    """Obtener mantenimientos programados en los próximos N días"""
    today = datetime.now().date()
    future_date = today + timedelta(days=days)

    upcoming = db.query(Maintenance)\
        .filter(
            Maintenance.status == MaintenanceStatusEnum.scheduled,
            Maintenance.scheduled_date >= today,
            Maintenance.scheduled_date <= future_date
        )\
        .order_by(Maintenance.scheduled_date.asc())\
        .all()

    return upcoming

@app.get("/overdue-maintenance", response_model=List[MaintenanceResponse])
def get_overdue_maintenance(db: Session = Depends(get_db)):
    """Obtener mantenimientos vencidos (no completados después de la fecha programada)"""
    today = datetime.now().date()

    overdue = db.query(Maintenance)\
        .filter(
            Maintenance.status == MaintenanceStatusEnum.scheduled,
            Maintenance.scheduled_date < today
        )\
        .order_by(Maintenance.scheduled_date.asc())\
        .all()

    return overdue

# ============================================
# ESTADÍSTICAS
# ============================================

@app.get("/stats/by-type")
def get_stats_by_type(db: Session = Depends(get_db)):
    """Estadísticas de mantenimiento por tipo"""
    stats = db.query(
        Maintenance.type,
        func.count(Maintenance.id).label('count'),
        func.sum(Maintenance.cost).label('total_cost')
    ).group_by(Maintenance.type).all()

    return [{
        "type": stat.type,
        "count": stat.count,
        "total_cost": float(stat.total_cost) if stat.total_cost else 0
    } for stat in stats]

@app.get("/stats/by-status")
def get_stats_by_status(db: Session = Depends(get_db)):
    """Estadísticas de mantenimiento por estado"""
    stats = db.query(
        Maintenance.status,
        func.count(Maintenance.id).label('count')
    ).group_by(Maintenance.status).all()

    return [{"status": stat.status, "count": stat.count} for stat in stats]

@app.get("/stats/costs-by-month")
def get_costs_by_month(year: Optional[int] = None, db: Session = Depends(get_db)):
    """Costos de mantenimiento por mes"""
    if not year:
        year = datetime.now().year

    stats = db.query(
        extract('month', Maintenance.performed_date).label('month'),
        func.sum(Maintenance.cost).label('total_cost'),
        func.count(Maintenance.id).label('count')
    ).filter(
        extract('year', Maintenance.performed_date) == year,
        Maintenance.status == MaintenanceStatusEnum.completed
    ).group_by(extract('month', Maintenance.performed_date))\
     .order_by('month').all()

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    return [{
        "month": months[int(stat.month) - 1] if stat.month else 'Unknown',
        "month_number": int(stat.month) if stat.month else 0,
        "total_cost": float(stat.total_cost) if stat.total_cost else 0,
        "count": stat.count
    } for stat in stats]

@app.get("/stats/equipment-maintenance-frequency")
def get_equipment_maintenance_frequency(limit: int = 10, db: Session = Depends(get_db)):
    """Equipos con más mantenimientos"""
    stats = db.query(
        Maintenance.equipment_id,
        func.count(Maintenance.id).label('maintenance_count'),
        func.sum(Maintenance.cost).label('total_cost')
    ).group_by(Maintenance.equipment_id)\
     .order_by(func.count(Maintenance.id).desc())\
     .limit(limit).all()

    return [{
        "equipment_id": stat.equipment_id,
        "maintenance_count": stat.maintenance_count,
        "total_cost": float(stat.total_cost) if stat.total_cost else 0
    } for stat in stats]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
