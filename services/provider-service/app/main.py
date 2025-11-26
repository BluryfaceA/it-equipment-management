from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import time
from .database import get_db, engine, Base
from .models import Provider, Contract, ContractStatus

app = FastAPI(title="Provider Service", version="1.0.0")

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

class ProviderCreate(BaseModel):
    name: str
    ruc: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    website: Optional[str] = None
    created_by: Optional[int] = None

class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    ruc: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None

class ProviderResponse(BaseModel):
    id: int
    name: str
    ruc: Optional[str]
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    website: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ContractCreate(BaseModel):
    provider_id: int
    contract_number: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    amount: Optional[Decimal] = None
    attachment_url: Optional[str] = None

class ContractUpdate(BaseModel):
    description: Optional[str] = None
    end_date: Optional[date] = None
    amount: Optional[Decimal] = None
    status: Optional[ContractStatus] = None
    attachment_url: Optional[str] = None

class ContractResponse(BaseModel):
    id: int
    provider_id: int
    contract_number: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    amount: Optional[Decimal]
    status: str
    attachment_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProviderWithContracts(ProviderResponse):
    contracts: List[ContractResponse] = []

# ============================================
# ENDPOINTS - PROVIDERS
# ============================================

@app.get("/")
def read_root():
    return {"service": "Provider Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    # Verificar si el RUC ya existe
    if provider.ruc:
        existing = db.query(Provider).filter(Provider.ruc == provider.ruc).first()
        if existing:
            raise HTTPException(status_code=400, detail="RUC already registered")

    db_provider = Provider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@app.get("/providers", response_model=List[ProviderResponse])
def get_providers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Provider)

    if is_active is not None:
        query = query.filter(Provider.is_active == is_active)

    if search:
        query = query.filter(
            or_(
                Provider.name.like(f"%{search}%"),
                Provider.ruc.like(f"%{search}%"),
                Provider.contact_person.like(f"%{search}%")
            )
        )

    providers = query.offset(skip).limit(limit).all()
    return providers

@app.get("/providers/{provider_id}", response_model=ProviderWithContracts)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@app.put("/providers/{provider_id}", response_model=ProviderResponse)
def update_provider(
    provider_id: int,
    provider_update: ProviderUpdate,
    db: Session = Depends(get_db)
):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    update_data = provider_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)

    db.commit()
    db.refresh(provider)
    return provider

@app.delete("/providers/{provider_id}")
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Verificar si tiene contratos activos
    active_contracts = db.query(Contract).filter(
        Contract.provider_id == provider_id,
        Contract.status == ContractStatus.ACTIVE
    ).count()

    if active_contracts > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete provider with active contracts"
        )

    db.delete(provider)
    db.commit()
    return {"message": "Provider deleted successfully"}

# ============================================
# ENDPOINTS - CONTRACTS
# ============================================

@app.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    # Verificar que el proveedor existe
    provider = db.query(Provider).filter(Provider.id == contract.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Verificar si el número de contrato ya existe
    existing = db.query(Contract).filter(
        Contract.contract_number == contract.contract_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Contract number already exists")

    db_contract = Contract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@app.get("/contracts", response_model=List[ContractResponse])
def get_contracts(
    skip: int = 0,
    limit: int = 100,
    provider_id: Optional[int] = None,
    status: Optional[ContractStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Contract)

    if provider_id:
        query = query.filter(Contract.provider_id == provider_id)
    if status:
        query = query.filter(Contract.status == status)

    contracts = query.offset(skip).limit(limit).all()
    return contracts

@app.get("/contracts/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@app.put("/contracts/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    contract_update: ContractUpdate,
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    update_data = contract_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)
    return contract

@app.delete("/contracts/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    db.delete(contract)
    db.commit()
    return {"message": "Contract deleted successfully"}

@app.get("/providers/{provider_id}/purchase-history")
def get_provider_purchase_history(provider_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial de compras de un proveedor"""
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Aquí se podría hacer un query a la tabla de equipos para obtener las compras
    # Para este ejemplo, retornamos los contratos
    contracts = db.query(Contract).filter(Contract.provider_id == provider_id).all()

    total_contracts = len(contracts)
    total_amount = sum(c.amount for c in contracts if c.amount) or 0

    return {
        "provider_id": provider_id,
        "provider_name": provider.name,
        "total_contracts": total_contracts,
        "total_amount": float(total_amount),
        "contracts": contracts
    }

@app.get("/stats/top-providers")
def get_top_providers(limit: int = 10, db: Session = Depends(get_db)):
    """Obtiene los proveedores con más contratos"""
    stats = db.query(
        Provider.id,
        Provider.name,
        func.count(Contract.id).label('contract_count'),
        func.sum(Contract.amount).label('total_amount')
    ).join(Contract, Contract.provider_id == Provider.id)\
     .group_by(Provider.id, Provider.name)\
     .order_by(func.count(Contract.id).desc())\
     .limit(limit).all()

    return [{
        "provider_id": stat.id,
        "provider_name": stat.name,
        "contract_count": stat.contract_count,
        "total_amount": float(stat.total_amount) if stat.total_amount else 0
    } for stat in stats]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
