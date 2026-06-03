from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_current_user, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import LoginRequest, SessionUser, TokenResponse

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash) or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credenciales invalidas.')
    token = create_access_token(user.email)
    return TokenResponse(access_token=token, user=SessionUser.model_validate(user))

@router.get('/me', response_model=SessionUser)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return SessionUser.model_validate(current_user)
