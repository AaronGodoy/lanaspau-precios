from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Supplier, User
from app.modules.auth.router import get_current_user
from app.modules.suppliers.schemas import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    suppliers = db.scalars(select(Supplier).order_by(Supplier.nombre)).all()
    return suppliers

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_in: SupplierCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    db_supplier = Supplier(**supplier_in.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_in: SupplierUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    db_supplier = db.scalar(select(Supplier).where(Supplier.id == supplier_id))
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        
    update_data = supplier_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_supplier, key, value)
        
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    db_supplier = db.scalar(select(Supplier).where(Supplier.id == supplier_id))
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        
    db.delete(db_supplier)
    db.commit()
