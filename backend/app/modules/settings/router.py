from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_admin
from app.db.database import get_db
from app.db.models import PriceSetting, User
from app.schemas.settings import SettingsResponse, SettingsUpdate
from app.services.audit_service import log_change
from app.utils.bootstrap import ensure_default_settings

router = APIRouter(prefix='/settings', tags=['Configuracion'])

@router.get('', response_model=SettingsResponse)
def get_settings(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    return ensure_default_settings(db)

@router.put('', response_model=SettingsResponse, dependencies=[Depends(require_admin)])
def update_settings(payload: SettingsUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    config = db.scalar(select(PriceSetting).limit(1)) or ensure_default_settings(db)
    for field, value in payload.model_dump().items():
        setattr(config, field, value)
    log_change(db, current_user.id, 'price_settings', config.id, 'editar', 'Configuracion general actualizada.')
    db.commit()
    db.refresh(config)
    return config
