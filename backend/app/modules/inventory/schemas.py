from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class InventoryMovementCreate(BaseModel):
    producto_id: int
    tipo: str = Field(..., description="Puede ser 'ingreso', 'merma', 'devolucion', 'ajuste'")
    cantidad: int
    costo_unitario: Optional[float] = None
    motivo: Optional[str] = None

class InventoryMovementResponse(BaseModel):
    id: int
    producto_id: int
    tipo: str
    cantidad: int
    costo_unitario: Optional[float]
    motivo: Optional[str]
    fecha: datetime
    usuario_id: Optional[int]

    class Config:
        from_attributes = True
