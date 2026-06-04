from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.database import get_db
from app.db.models import InventoryMovement, Product, User
from app.modules.auth.router import get_current_user
from app.modules.inventory.schemas import InventoryMovementCreate, InventoryMovementResponse

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/movements", response_model=List[InventoryMovementResponse])
def get_movements(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 50
):
    movements = db.scalars(select(InventoryMovement).order_by(desc(InventoryMovement.fecha)).limit(limit)).all()
    return movements

@router.post("/movements", response_model=InventoryMovementResponse, status_code=status.HTTP_201_CREATED)
def register_movement(
    movement_in: InventoryMovementCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Verificar que el producto existe
    product = db.scalar(select(Product).where(Product.id == movement_in.producto_id))
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # Validaciones según tipo
    if movement_in.tipo not in ['ingreso', 'merma', 'devolucion', 'ajuste']:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido")
        
    if movement_in.tipo == 'merma' and movement_in.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad de merma debe ser positiva")
        
    # Crear registro de movimiento
    db_movement = InventoryMovement(
        producto_id=movement_in.producto_id,
        tipo=movement_in.tipo,
        cantidad=movement_in.cantidad,
        costo_unitario=movement_in.costo_unitario,
        motivo=movement_in.motivo,
        usuario_id=current_user.id
    )
    db.add(db_movement)
    
    # Actualizar stock del producto
    if movement_in.tipo == 'ingreso':
        product.stock += movement_in.cantidad
        # Si es ingreso y trae costo, podríamos actualizar el costo del producto (opcional, por ahora lo guardamos en el movimiento)
    elif movement_in.tipo == 'merma':
        # Asegurar que no quede stock negativo (opcional, a veces las mermas se registran post-venta)
        product.stock -= movement_in.cantidad
    elif movement_in.tipo == 'devolucion':
        product.stock += movement_in.cantidad
    elif movement_in.tipo == 'ajuste':
        # Ajuste puede ser positivo o negativo, lo sumamos directamente (si envían -5, resta 5)
        product.stock += movement_in.cantidad
        
    db.commit()
    db.refresh(db_movement)
    return db_movement
