from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SessionUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    email: EmailStr
    rol: str
    activo: bool
    fecha_creacion: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: SessionUser
