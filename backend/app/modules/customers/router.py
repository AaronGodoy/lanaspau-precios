from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Customer, User
from app.schemas.customers import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(prefix='/customers', tags=['Clientes'])

@router.get('', response_model=list[CustomerResponse])
def list_customers(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], q: str | None = Query(default=None), include_inactive: bool = False):
    query = select(Customer)
    if not include_inactive:
        query = query.where(Customer.activo.is_(True))
    if q:
        term = f'%{q.strip()}%'
        query = query.where(or_(Customer.nombre.ilike(term), Customer.rut.ilike(term), Customer.email.ilike(term)))
    customers = db.scalars(query.order_by(Customer.fecha_creacion.desc())).all()
    return customers

@router.post('', response_model=CustomerResponse)
def create_customer(payload: CustomerCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if payload.rut:
        exists = db.scalar(select(Customer).where(Customer.rut == payload.rut))
        if exists:
            raise HTTPException(status_code=400, detail='El RUT ya está registrado.')
    
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.put('/{customer_id}', response_model=CustomerResponse)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail='Cliente no encontrado.')
        
    updates = payload.model_dump(exclude_unset=True)
    if 'rut' in updates and updates['rut']:
        exists = db.scalar(select(Customer).where(Customer.rut == updates['rut'], Customer.id != customer_id))
        if exists:
            raise HTTPException(status_code=400, detail='El RUT ya está registrado por otro cliente.')
            
    for field, value in updates.items():
        setattr(customer, field, value)
        
    db.commit()
    db.refresh(customer)
    return customer

@router.delete('/{customer_id}')
def deactivate_customer(customer_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail='Cliente no encontrado.')
    customer.activo = False
    db.commit()
    return {'message': 'Cliente desactivado correctamente.'}
