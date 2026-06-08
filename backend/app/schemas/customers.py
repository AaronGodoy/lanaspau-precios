from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class CustomerBase(BaseModel):
    rut: str | None = Field(default=None, max_length=20)
    nombre: str = Field(min_length=2, max_length=150)
    telefono: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    direccion: str | None = None
    activo: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    rut: str | None = Field(default=None, max_length=20)
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    telefono: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    direccion: str | None = None
    activo: bool | None = None

class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_creacion: datetime
