from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class SaleItemCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

class SaleCreate(BaseModel):
    metodo_pago: Optional[str] = None
    notas: Optional[str] = None
    items: List[SaleItemCreate]

class SaleItemResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    
    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    total: float
    metodo_pago: Optional[str]
    fecha_venta: datetime
    notas: Optional[str]
    items: List[SaleItemResponse]
    
    class Config:
        from_attributes = True

class LowStockAlert(BaseModel):
    producto_id: int
    codigo_producto: str
    nombre: str
    stock_actual: int
    stock_minimo: int
    
    class Config:
        from_attributes = True
