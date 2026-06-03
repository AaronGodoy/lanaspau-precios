from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import PriceSetting, User

def ensure_default_settings(db: Session) -> PriceSetting:
    config = db.scalar(select(PriceSetting).limit(1))
    if config:
        return config
    config = PriceSetting(margen_minimo_porcentaje=20, margen_recomendado_porcentaje=35, margen_premium_porcentaje=45, iva_porcentaje_default=19, redondeo_precio='100', moneda='CLP', costos_fijos_generales=0)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config

def ensure_admin_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == settings.default_admin_email.lower()))
    if user:
        return user
    user = User(nombre='Administrador lanaspau', email=settings.default_admin_email.lower(), password_hash=get_password_hash(settings.default_admin_password), rol='administrador', activo=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
