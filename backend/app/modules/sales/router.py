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

@router.get("/stats/dashboard")
def get_dashboard_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta
    
    # 1. Ventas de hoy
    today = datetime.utcnow().date()
    ventas_hoy = db.scalar(
        select(func.sum(Sale.total))
        .where(func.date(Sale.fecha_venta) == today)
    ) or 0

    # 2. Productos vendidos hoy
    productos_hoy = db.scalar(
        select(func.sum(SaleItem.cantidad))
        .join(Sale)
        .where(func.date(Sale.fecha_venta) == today)
    ) or 0

    # 3. Ventas últimos 7 días (para gráfico)
    seven_days_ago = today - timedelta(days=6)
    ventas_por_dia = db.execute(
        select(
            func.date(Sale.fecha_venta).label('fecha'),
            func.sum(Sale.total).label('total')
        )
        .where(func.date(Sale.fecha_venta) >= seven_days_ago)
        .group_by(func.date(Sale.fecha_venta))
        .order_by(func.date(Sale.fecha_venta))
    ).all()

    # Rellenar días vacíos
    grafico_ventas = []
    ventas_dict = {str(row.fecha): float(row.total) for row in ventas_por_dia}
    for i in range(7):
        current_date = seven_days_ago + timedelta(days=i)
        date_str = str(current_date)
        grafico_ventas.append({
            "name": current_date.strftime("%A")[:3], # Lun, Mar, Mie...
            "total": ventas_dict.get(date_str, 0)
        })

    # 4. Productos más vendidos (Top 5 histórico)
    top_productos = db.execute(
        select(
            Product.nombre,
            func.sum(SaleItem.cantidad).label('total_vendido')
        )
        .join(SaleItem, SaleItem.producto_id == Product.id)
        .group_by(Product.id, Product.nombre)
        .order_by(desc('total_vendido'))
        .limit(5)
    ).all()

    grafico_top_productos = [
        {"name": row.nombre[:15] + "..." if len(row.nombre) > 15 else row.nombre, "cantidad": int(row.total_vendido)}
        for row in top_productos
    ]

    # Inversión total (costo * stock)
    inversion_total = db.scalar(
        select(func.sum(Product.stock * Product.latest_cost_total))
        .where(Product.stock > 0)
        .where(Product.latest_cost_total != None)
    ) or 0
    
    # Venta potencial (precio_recomendado * stock)
    venta_potencial = db.scalar(
        select(func.sum(Product.stock * Product.latest_recommended_price))
        .where(Product.stock > 0)
        .where(Product.latest_recommended_price != None)
    ) or 0

    return {
        "ventas_hoy": float(ventas_hoy),
        "productos_hoy": int(productos_hoy),
        "grafico_ventas": grafico_ventas,
        "grafico_top_productos": grafico_top_productos,
        "inversion_total": float(inversion_total),
        "venta_potencial": float(venta_potencial),
        "ganancia_estimada": float(venta_potencial - inversion_total)
    }
