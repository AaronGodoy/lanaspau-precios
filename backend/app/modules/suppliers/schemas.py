from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SupplierBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None
    activo: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None

class SupplierResponse(SupplierBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True
