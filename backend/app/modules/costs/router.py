from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import PriceSetting, Product, ProductCost, User
from app.schemas.products import ProductCostCreate, ProductCostResponse
from app.services.audit_service import log_change
from app.services.pricing_service import create_calculated_price, create_cost_from_input, serialize_cost

router = APIRouter(prefix='/costs', tags=['Costos'])

@router.post('', response_model=dict)
def create_cost(payload: ProductCostCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, payload.producto_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    settings = db.scalar(select(PriceSetting).limit(1))
    costs, pricing = create_cost_from_input(payload, settings, product=product)
    cost = ProductCost(producto_id=payload.producto_id, valor_compra_neto=costs['valor_compra_neto'], iva_porcentaje=costs['iva_porcentaje'], valor_iva=costs['valor_iva'], valor_compra_bruto=costs['valor_compra_bruto'], compra_incluye_iva=payload.compra_incluye_iva, costo_envio=payload.costo_envio, costo_retiro=payload.costo_retiro, otros_costos=payload.otros_costos, costo_total=costs['costo_total'], fecha_compra=payload.fecha_compra)
    
    # Update product stock
    cantidad = getattr(payload, 'cantidad', 1)
    product.stock += cantidad
    
    db.add(cost)
    db.flush()
    db.add(create_calculated_price(payload.producto_id, costs['costo_total'], settings, product=product))
    log_change(db, current_user.id, 'product_costs', cost.id, 'crear', f'Costo registrado para {product.codigo_producto}.')
    db.commit()
    db.refresh(cost)
    return {'cost': serialize_cost(cost), 'pricing': pricing}

@router.get('/product/{product_id}', response_model=list[ProductCostResponse])
def list_product_costs(product_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    costs = db.scalars(select(ProductCost).where(ProductCost.producto_id == product_id).order_by(ProductCost.fecha_compra.desc(), ProductCost.id.desc())).all()
    return [ProductCostResponse(**serialize_cost(cost)) for cost in costs]
