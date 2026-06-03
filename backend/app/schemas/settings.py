from pydantic import BaseModel, ConfigDict, Field

class SettingsUpdate(BaseModel):
    margen_minimo_porcentaje: float = Field(ge=0, lt=100)
    margen_recomendado_porcentaje: float = Field(ge=0, lt=100)
    margen_premium_porcentaje: float = Field(ge=0, lt=100)
    iva_porcentaje_default: float = Field(ge=0, le=100)
    redondeo_precio: str = Field(pattern='^(ninguno|100|500|1000)$')
    moneda: str = Field(default='CLP', max_length=10)
    costos_fijos_generales: float = Field(default=0, ge=0)

class SettingsResponse(SettingsUpdate):
    model_config = ConfigDict(from_attributes=True)
    id: int
