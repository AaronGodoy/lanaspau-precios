from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_admin
from app.db.database import get_db
from app.db.models import CashRegister, Sale, User
from app.schemas.cash_registers import CashRegisterClose, CashRegisterCreate, CashRegisterResponse

router = APIRouter(prefix='/cash-registers', tags=['Caja'])

@router.get('/current', response_model=CashRegisterResponse | None)
def get_current_cash_register(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    caja = db.scalar(select(CashRegister).where(CashRegister.estado == 'abierta', CashRegister.usuario_id == current_user.id).order_by(CashRegister.fecha_apertura.desc()))
    return caja

@router.post('/open', response_model=CashRegisterResponse)
def open_cash_register(payload: CashRegisterCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    existing = db.scalar(select(CashRegister).where(CashRegister.estado == 'abierta', CashRegister.usuario_id == current_user.id))
    if existing:
        raise HTTPException(status_code=400, detail='Ya tienes una caja abierta. Ciérrala antes de abrir una nueva.')
        
    caja = CashRegister(
        usuario_id=current_user.id,
        monto_inicial=payload.monto_inicial,
        notas=payload.notas,
        estado='abierta'
    )
    db.add(caja)
    db.commit()
    db.refresh(caja)
    return caja

@router.post('/{caja_id}/close', response_model=CashRegisterResponse)
def close_cash_register(caja_id: int, payload: CashRegisterClose, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    caja = db.get(CashRegister, caja_id)
    if not caja:
        raise HTTPException(status_code=404, detail='Caja no encontrada.')
    if caja.estado == 'cerrada':
        raise HTTPException(status_code=400, detail='La caja ya está cerrada.')
    if caja.usuario_id != current_user.id and current_user.rol != 'administrador':
        raise HTTPException(status_code=403, detail='No tienes permiso para cerrar esta caja.')
        
    # Calculate expected final amount
    # Only sum cash sales? Let's assume we sum all sales for now, or just cash. 
    # Usually cash register difference is calculated against 'Efectivo'.
    cash_sales_total = db.scalar(
        select(func.sum(Sale.total))
        .where(Sale.caja_id == caja.id, Sale.metodo_pago == 'efectivo')
    ) or 0
    
    monto_final_esperado = float(caja.monto_inicial) + float(cash_sales_total)
    diferencia = payload.monto_final_real - monto_final_esperado
    
    caja.monto_final_esperado = monto_final_esperado
    caja.monto_final_real = payload.monto_final_real
    caja.diferencia = diferencia
    if payload.notas:
        caja.notas = f"{caja.notas or ''} | Cierre: {payload.notas}"
    caja.fecha_cierre = datetime.utcnow()
    caja.estado = 'cerrada'
    
    db.commit()
    db.refresh(caja)
    return caja

@router.get('', response_model=list[CashRegisterResponse], dependencies=[Depends(require_admin)])
def list_cash_registers(db: Annotated[Session, Depends(get_db)]):
    cajas = db.scalars(select(CashRegister).order_by(CashRegister.fecha_apertura.desc())).all()
    return cajas
