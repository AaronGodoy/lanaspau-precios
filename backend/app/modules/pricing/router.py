from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import CalculatedPrice, PriceSetting, Product, ProductCost, User
from app.schemas.pricing import LiveCalculationInput, PriceCalculationResponse
from app.schemas.reports import DashboardItem, DashboardResponse
from app.services.audit_service import log_change
from app.services.pricing_service import build_explanation, create_calculated_price, create_cost_from_input, serialize_price_history, to_float

router = APIRouter(prefix='/pricing', tags=['Pricing'])

@router.post('/calculate', response_model=PriceCalculationResponse)
def calculate(payload: LiveCalculationInput, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    settings = db.scalar(select(PriceSetting).limit(1))
    product = None
    if payload.producto_id:
        product = db.get(Product, payload.producto_id)
        
    costs, pricing = create_cost_from_input(payload, settings, product=product)
    response = {'producto_id': payload.producto_id, **{key: costs[key] for key in ('valor_compra_neto', 'iva_porcentaje', 'valor_iva', 'valor_compra_bruto', 'costo_total')}, **pricing, 'explicacion': build_explanation(costs, settings, pricing, product=product), 'fecha_calculo': datetime.utcnow()}
    return PriceCalculationResponse(**response)

@router.post('/product/{product_id}/recalculate', response_model=dict)
def recalculate_product(product_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    latest_cost = db.scalar(select(ProductCost).where(ProductCost.producto_id == product_id).order_by(ProductCost.fecha_compra.desc(), ProductCost.id.desc()))
    if not latest_cost:
        raise HTTPException(status_code=400, detail='El producto no tiene costos registrados.')
    settings = db.scalar(select(PriceSetting).limit(1))
    new_price = create_calculated_price(product_id, float(latest_cost.costo_total), settings, product=product)
    db.add(new_price)
    db.flush()
    log_change(db, current_user.id, 'calculated_prices', new_price.id, 'recalcular', f'Precio recalculado para {product.codigo_producto}.')
    db.commit()
    db.refresh(new_price)
    return serialize_price_history(new_price)

@router.get('/product/{product_id}/history', response_model=list[dict])
def get_price_history(product_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    history = db.scalars(select(CalculatedPrice).where(CalculatedPrice.producto_id == product_id).order_by(CalculatedPrice.fecha_calculo.desc(), CalculatedPrice.id.desc())).all()
    return [serialize_price_history(item) for item in history]

@router.get('/dashboard', response_model=DashboardResponse)
def dashboard(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    products = db.scalars(select(Product).where(Product.activo.is_(True)).order_by(Product.fecha_creacion.desc())).all()
    latest_rows = []
    
    total_invertido = 0.0
    potencial_venta = 0.0
    
    for product in products:
        latest_cost = db.scalar(select(ProductCost).where(ProductCost.producto_id == product.id).order_by(ProductCost.fecha_compra.desc(), ProductCost.id.desc()))
        latest_price = db.scalar(select(CalculatedPrice).where(CalculatedPrice.producto_id == product.id).order_by(CalculatedPrice.fecha_calculo.desc(), CalculatedPrice.id.desc()))
        
        costo_unitario = to_float(latest_cost.costo_total) if latest_cost else None
        precio_rec_unitario = to_float(latest_price.precio_recomendado) if latest_price else None
        margen = to_float(latest_price.margen_estimado) if latest_price else None
        
        stock_actual = product.stock if product.stock else 0
        
        if costo_unitario is not None:
            total_invertido += (costo_unitario * stock_actual)
            
        if precio_rec_unitario is not None:
            potencial_venta += (precio_rec_unitario * stock_actual)
            
        latest_rows.append({
            'producto_id': product.id, 
            'codigo_producto': product.codigo_producto, 
            'nombre': product.nombre, 
            'categoria': product.categoria, 
            'costo_total': costo_unitario, 
            'precio_recomendado': precio_rec_unitario, 
            'margen_estimado': margen, 
            'fecha': latest_price.fecha_calculo if latest_price else product.fecha_creacion
        })
        
    rows_with_margin = [row for row in latest_rows if row['margen_estimado'] is not None]
    total_products = len(products)
    
    promedio_margen = round(sum(row['margen_estimado'] for row in rows_with_margin) / len(rows_with_margin), 2) if rows_with_margin else 0
    
    mejor = [DashboardItem(**row) for row in sorted(rows_with_margin, key=lambda row: row['margen_estimado'], reverse=True)[:5]]
    peor = [DashboardItem(**row) for row in sorted(rows_with_margin, key=lambda row: row['margen_estimado'])[:5]]
    ultimos = [DashboardItem(**row) for row in latest_rows[:5]]
    
    return DashboardResponse(
        total_productos=total_products, 
        promedio_margen=promedio_margen, 
        total_invertido_inventario=round(total_invertido, 2), 
        valor_potencial_venta=round(potencial_venta, 2), 
        productos_mejor_margen=mejor, 
        productos_menor_margen=peor, 
        ultimos_productos=ultimos
    )
