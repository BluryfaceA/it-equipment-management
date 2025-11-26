from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import time
from .database import get_db, engine, Base
from .models import Equipment, EquipmentCategory, Location, EquipmentLocationHistory, EquipmentStatus

app = FastAPI(title="Equipment Service", version="1.0.0")

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

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

class LocationCreate(BaseModel):
    building: str
    floor: Optional[str] = None
    room: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None

class LocationResponse(BaseModel):
    id: int
    building: str
    floor: Optional[str]
    room: Optional[str]
    department: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

class EquipmentCreate(BaseModel):
    asset_code: str
    serial_number: Optional[str] = None
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    provider_id: Optional[int] = None
    warranty_months: int = 12
    current_location_id: Optional[int] = None
    assigned_to: Optional[str] = None
    specifications: Optional[dict] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None

class EquipmentUpdate(BaseModel):
    serial_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    assigned_to: Optional[str] = None
    specifications: Optional[dict] = None
    notes: Optional[str] = None

class EquipmentResponse(BaseModel):
    id: int
    asset_code: str
    serial_number: Optional[str]
    name: str
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    purchase_date: Optional[date]
    purchase_price: Optional[Decimal]
    status: str
    assigned_to: Optional[str]
    category: Optional[CategoryResponse]
    location: Optional[LocationResponse]
    warranty_end_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True

class EquipmentMove(BaseModel):
    location_id: int
    assigned_to: Optional[str] = None
    move_date: date
    reason: Optional[str] = None
    moved_by: Optional[int] = None

class LocationHistoryResponse(BaseModel):
    id: int
    equipment_id: int
    location: LocationResponse
    assigned_to: Optional[str]
    move_date: date
    reason: Optional[str]

    class Config:
        from_attributes = True

# ============================================
# EQUIPMENT CATEGORIES
# ============================================

@app.get("/")
def read_root():
    return {"service": "Equipment Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = EquipmentCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories", response_model=List[CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(EquipmentCategory).offset(skip).limit(limit).all()
    return categories

@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(EquipmentCategory).filter(EquipmentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# ============================================
# LOCATIONS
# ============================================

@app.post("/locations", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    db_location = Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@app.get("/locations", response_model=List[LocationResponse])
def get_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = db.query(Location).offset(skip).limit(limit).all()
    return locations

@app.get("/locations/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

# ============================================
# EQUIPMENT
# ============================================

@app.post("/equipment", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    # Verificar si el código de activo ya existe
    existing = db.query(Equipment).filter(Equipment.asset_code == equipment.asset_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Asset code already exists")

    # Calcular fecha de fin de garantía
    warranty_end = None
    if equipment.purchase_date and equipment.warranty_months:
        from dateutil.relativedelta import relativedelta
        warranty_end = equipment.purchase_date + relativedelta(months=equipment.warranty_months)

    db_equipment = Equipment(
        **equipment.model_dump(exclude={'warranty_months'}),
        warranty_months=equipment.warranty_months,
        warranty_end_date=warranty_end
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)

    # Registrar ubicación inicial en historial
    if equipment.current_location_id:
        history = EquipmentLocationHistory(
            equipment_id=db_equipment.id,
            location_id=equipment.current_location_id,
            assigned_to=equipment.assigned_to,
            move_date=datetime.now().date(),
            reason="Initial registration",
            moved_by=equipment.created_by
        )
        db.add(history)
        db.commit()

    return db_equipment

@app.get("/equipment", response_model=List[EquipmentResponse])
def get_equipment(
    skip: int = 0,
    limit: int = 100,
    status: Optional[EquipmentStatus] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Equipment)

    if status:
        query = query.filter(Equipment.status == status)
    if category_id:
        query = query.filter(Equipment.category_id == category_id)
    if location_id:
        query = query.filter(Equipment.current_location_id == location_id)
    if search:
        query = query.filter(
            or_(
                Equipment.name.like(f"%{search}%"),
                Equipment.asset_code.like(f"%{search}%"),
                Equipment.serial_number.like(f"%{search}%"),
                Equipment.brand.like(f"%{search}%"),
                Equipment.model.like(f"%{search}%")
            )
        )

    equipment_list = query.offset(skip).limit(limit).all()
    return equipment_list

@app.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
def get_equipment_by_id(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@app.put("/equipment/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(equipment_id: int, equipment_update: EquipmentUpdate, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    update_data = equipment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)
    return equipment

@app.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    db.delete(equipment)
    db.commit()
    return {"message": "Equipment deleted successfully"}

@app.post("/equipment/{equipment_id}/move", response_model=EquipmentResponse)
def move_equipment(equipment_id: int, move: EquipmentMove, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Actualizar ubicación actual
    equipment.current_location_id = move.location_id
    equipment.assigned_to = move.assigned_to

    # Registrar en historial
    history = EquipmentLocationHistory(
        equipment_id=equipment_id,
        location_id=move.location_id,
        assigned_to=move.assigned_to,
        move_date=move.move_date,
        reason=move.reason,
        moved_by=move.moved_by
    )
    db.add(history)
    db.commit()
    db.refresh(equipment)

    return equipment

@app.get("/equipment/{equipment_id}/history", response_model=List[LocationHistoryResponse])
def get_equipment_history(equipment_id: int, db: Session = Depends(get_db)):
    history = db.query(EquipmentLocationHistory)\
        .filter(EquipmentLocationHistory.equipment_id == equipment_id)\
        .order_by(EquipmentLocationHistory.move_date.desc())\
        .all()
    return history

@app.get("/stats/by-status")
def get_stats_by_status(db: Session = Depends(get_db)):
    stats = db.query(
        Equipment.status,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.status).all()

    return [{"status": stat.status, "count": stat.count} for stat in stats]

@app.get("/stats/by-category")
def get_stats_by_category(db: Session = Depends(get_db)):
    stats = db.query(
        EquipmentCategory.name,
        func.count(Equipment.id).label('count')
    ).join(Equipment, Equipment.category_id == EquipmentCategory.id)\
     .group_by(EquipmentCategory.name).all()

    return [{"category": stat.name, "count": stat.count} for stat in stats]

@app.get("/stats/by-location")
def get_stats_by_location(db: Session = Depends(get_db)):
    stats = db.query(
        Location.building,
        Location.department,
        func.count(Equipment.id).label('count')
    ).join(Equipment, Equipment.current_location_id == Location.id)\
     .group_by(Location.building, Location.department).all()

    return [{
        "building": stat.building,
        "department": stat.department,
        "count": stat.count
    } for stat in stats]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
