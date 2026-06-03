from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta or settings.access_token_expire_minutes)
    return jwt.encode({'sub': subject, 'exp': expire}, settings.secret_key, algorithm=settings.algorithm)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='No se pudo validar la sesion.', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get('sub')
        if not email:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    user = db.scalar(select(User).where(User.email == email))
    if not user or not user.activo:
        raise credentials_exception
    return user

def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.rol != 'administrador':
        raise HTTPException(status_code=403, detail='Este recurso requiere rol administrador.')
    return current_user
