from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=120)
    rol: str = Field(default='usuario', pattern='^(administrador|usuario)$')
    activo: bool = True

class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    rol: str | None = Field(default=None, pattern='^(administrador|usuario)$')
    activo: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=120)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool
    fecha_creacion: datetime
