from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Product, Sale, SaleItem, User
from app.modules.auth.router import get_current_user
from app.modules.sales.schemas import SaleCreate, SaleResponse, LowStockAlert

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate, 
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not sale_data.items:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto")
        
    # Calcular total y verificar stock
    total_venta = 0
    sale_items_db = []
    
    for item in sale_data.items:
        producto = db.scalar(select(Product).where(Product.id == item.producto_id))
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto ID {item.producto_id} no encontrado")
            
        if producto.stock < item.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente para {producto.nombre}. Stock actual: {producto.stock}"
            )
            
        subtotal = item.cantidad * item.precio_unitario
        total_venta += subtotal
        
        # Descontar stock
        producto.stock -= item.cantidad
        
        # Crear item de venta
        sale_item = SaleItem(
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=subtotal
        )
        sale_items_db.append(sale_item)
        
    # Crear la venta
    db_sale = Sale(
        usuario_id=current_user.id,
        total=total_venta,
        metodo_pago=sale_data.metodo_pago,
        notas=sale_data.notas,
        items=sale_items_db
    )
    
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    return db_sale

@router.get("/", response_model=List[SaleResponse])
def get_sales(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 50,
    offset: int = 0
):
    sales = db.scalars(select(Sale).order_by(Sale.fecha_venta.desc()).limit(limit).offset(offset)).unique().all()
    return sales

@router.get("/alerts/low-stock", response_model=List[LowStockAlert])
def get_low_stock_alerts(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Productos donde el stock actual es menor o igual al stock minimo
    alerts = db.execute(
        select(
            Product.id.label('producto_id'),
            Product.codigo_producto,
            Product.nombre,
            Product.stock.label('stock_actual'),
            Product.stock_minimo
        ).where(Product.stock <= Product.stock_minimo, Product.activo == True)
    ).mappings().all()
    
    return alerts
