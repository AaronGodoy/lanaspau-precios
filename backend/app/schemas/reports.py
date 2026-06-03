from datetime import datetime
from pydantic import BaseModel

class DashboardItem(BaseModel):
    producto_id: int
    codigo_producto: str
    nombre: str
    categoria: str | None = None
    costo_total: float | None = None
    precio_recomendado: float | None = None
    margen_estimado: float | None = None
    fecha: datetime | None = None

class DashboardResponse(BaseModel):
    total_productos: int
    promedio_margen: float
    total_invertido_inventario: float
    valor_potencial_venta: float
    productos_mejor_margen: list[DashboardItem]
    productos_menor_margen: list[DashboardItem]
    ultimos_productos: list[DashboardItem]
