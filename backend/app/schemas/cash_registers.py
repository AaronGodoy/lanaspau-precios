from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class CashRegisterBase(BaseModel):
    monto_inicial: float = Field(default=0, ge=0)
    notas: str | None = None

class CashRegisterCreate(CashRegisterBase):
    pass

class CashRegisterClose(BaseModel):
    monto_final_real: float = Field(ge=0)
    notas: str | None = None

class CashRegisterResponse(CashRegisterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    fecha_apertura: datetime
    fecha_cierre: datetime | None = None
    monto_final_esperado: float | None = None
    monto_final_real: float | None = None
    diferencia: float | None = None
    estado: str
