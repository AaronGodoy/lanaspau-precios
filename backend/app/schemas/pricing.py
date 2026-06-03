from datetime import datetime, date
from pydantic import BaseModel, Field

class LiveCalculationInput(BaseModel):
    producto_id: int | None = None
    cantidad: int = Field(default=1, gt=0)
    valor_compra: float = Field(gt=0)
    compra_incluye_iva: bool = False
    iva_porcentaje: float = Field(default=19, ge=0, le=100)
    costo_envio: float = Field(default=0, ge=0)
    costo_retiro: float = Field(default=0, ge=0)
    otros_costos: float = Field(default=0, ge=0)
    manual_margin_porcentaje: float | None = Field(default=None, ge=0, lt=100)
    redondeo_precio: str | None = Field(default=None, pattern='^(ninguno|100|500|1000)$')
    fecha_compra: date | None = None

class PriceCalculationResponse(BaseModel):
    producto_id: int | None = None
    valor_compra_neto: float
    iva_porcentaje: float
    valor_iva: float
    valor_compra_bruto: float
    costo_total: float
    precio_minimo: float
    precio_recomendado: float
    precio_premium: float
    margen_estimado: float
    utilidad_estimada: float
    manual_margin_porcentaje: float | None = None
    precio_personalizado: float | None = None
    utilidad_personalizada: float | None = None
    margen_real_personalizado: float | None = None
    explicacion: list[str]
    fecha_calculo: datetime | None = None
