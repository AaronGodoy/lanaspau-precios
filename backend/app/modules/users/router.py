from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import get_current_user, get_password_hash, require_admin
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from app.services.audit_service import log_change

router = APIRouter(prefix='/users', tags=['Usuarios'])

@router.get('/me', response_model=UserResponse)
def current_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.get('', response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(User).order_by(User.fecha_creacion.desc())).all()

@router.post('', response_model=UserResponse, dependencies=[Depends(require_admin)])
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    exists = db.scalar(select(User).where(User.email == payload.email.lower()))
    if exists:
        raise HTTPException(status_code=400, detail='Ya existe un usuario con ese email.')
    user = User(nombre=payload.nombre, email=payload.email.lower(), password_hash=get_password_hash(payload.password), rol=payload.rol, activo=payload.activo)
    db.add(user)
    db.flush()
    log_change(db, current_user.id, 'users', user.id, 'crear', f'Usuario {user.email} creado.')
    db.commit()
    db.refresh(user)
    return user

@router.put('/{user_id}', response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user(user_id: int, payload: UserUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='Usuario no encontrado.')
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == 'password' and value:
            user.password_hash = get_password_hash(value)
        else:
            setattr(user, field, value)
    log_change(db, current_user.id, 'users', user.id, 'editar', f'Usuario {user.email} actualizado.')
    db.commit()
    db.refresh(user)
    return user
