from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    codigo_producto: str | None = Field(default=None, max_length=50)
    nombre: str = Field(min_length=2, max_length=150)
    marca: str | None = Field(default=None, max_length=100)
    categoria: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=60)
    gramaje: str | None = Field(default=None, max_length=60)
    metros: float | None = None
    proveedor_id: int | None = None
    descripcion: str | None = None
    stock: int = Field(default=0, ge=0)
    margen_minimo_porcentaje: float | None = Field(default=None, ge=0, le=100)
    margen_recomendado_porcentaje: float | None = Field(default=None, ge=0, le=100)
    margen_premium_porcentaje: float | None = Field(default=None, ge=0, le=100)
    activo: bool = True

class ProductCreate(ProductBase):
    costo_inicial_total: float | None = Field(default=None, ge=0)
    compra_incluye_iva: bool = False

class ProductUpdate(BaseModel):
    codigo_producto: str | None = Field(default=None, min_length=2, max_length=50)
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    marca: str | None = Field(default=None, max_length=100)
    categoria: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=60)
    gramaje: str | None = Field(default=None, max_length=60)
    metros: float | None = None
    proveedor_id: int | None = None
    descripcion: str | None = None
    stock: int | None = Field(default=None, ge=0)
    margen_minimo_porcentaje: float | None = Field(default=None, ge=0, le=100)
    margen_recomendado_porcentaje: float | None = Field(default=None, ge=0, le=100)
    margen_premium_porcentaje: float | None = Field(default=None, ge=0, le=100)
    activo: bool | None = None

class SupplierBrief(BaseModel):
    id: int
    nombre: str

    model_config = ConfigDict(from_attributes=True)

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_creacion: datetime
    latest_cost_total: float | None = None
    latest_recommended_price: float | None = None
    proveedor_rel: SupplierBrief | None = None

class ProductCostCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(default=1, gt=0)
    valor_compra: float = Field(gt=0)
    compra_incluye_iva: bool = False
    iva_porcentaje: float | None = Field(default=None, ge=0, le=100)
    costo_envio: float = Field(default=0, ge=0)
    costo_retiro: float = Field(default=0, ge=0)
    otros_costos: float = Field(default=0, ge=0)
    fecha_compra: date | None = None

class ProductCostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    producto_id: int
    valor_compra_neto: float
    iva_porcentaje: float
    valor_iva: float
    valor_compra_bruto: float
    compra_incluye_iva: bool
    costo_envio: float
    costo_retiro: float
    otros_costos: float
    costo_total: float
    fecha_compra: date
