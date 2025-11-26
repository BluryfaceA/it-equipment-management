from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
import time
from .database import get_db, engine, Base
from .models import User, UserRole
from .auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Auth Service", version="1.0.0")

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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SCHEMAS (Pydantic Models)
# ============================================

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.viewer

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    return {"service": "Auth Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Endpoint de login"""
    user = db.query(User).filter(User.username == user_login.username).first()

    # Comparación directa de contraseñas (SIN HASH - solo para desarrollo)
    if not user or user.password_hash != user_login.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.post("/register", response_model=UserResponse)
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.admin]))
):
    """Registro de nuevos usuarios (solo admin)"""
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(
        (User.username == user_create.username) | (User.email == user_create.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Crear nuevo usuario (SIN HASH - solo para desarrollo)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=user_create.password,  # Contraseña en texto plano
        full_name=user_create.full_name,
        role=user_create.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

@app.put("/me/password")
def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    # Comparación directa (SIN HASH - solo para desarrollo)
    if current_user.password_hash != password_change.old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    current_user.password_hash = password_change.new_password
    db.commit()

    return {"message": "Password updated successfully"}

@app.get("/users", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.admin, UserRole.technician]))
):
    """Listar usuarios"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener usuario por ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.admin]))
):
    """Actualizar usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Actualizar campos
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.admin]))
):
    """Eliminar usuario (solo admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

@app.post("/verify-token", response_model=UserResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    """Verificar validez del token"""
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
