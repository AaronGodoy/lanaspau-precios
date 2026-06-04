from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.core.security import get_current_user, require_admin
from app.db.database import get_db
from app.db.models import CalculatedPrice, Product, ProductCost, User, PriceSetting
from app.schemas.products import ProductCreate, ProductResponse, ProductUpdate
from app.services.audit_service import log_change
from app.services.pricing_service import to_float, calculate_cost_breakdown, calculate_pricing_from_total

router = APIRouter(prefix='/products', tags=['Productos'])

def build_product_response(db: Session, product: Product) -> ProductResponse:
    latest_cost = db.scalar(select(ProductCost).where(ProductCost.producto_id == product.id).order_by(ProductCost.fecha_compra.desc(), ProductCost.id.desc()))
    latest_price = db.scalar(select(CalculatedPrice).where(CalculatedPrice.producto_id == product.id).order_by(CalculatedPrice.fecha_calculo.desc(), CalculatedPrice.id.desc()))
    
    data = {c.name: getattr(product, c.name) for c in product.__table__.columns}
    data['proveedor_rel'] = product.proveedor_rel
    data['latest_cost_total'] = to_float(latest_cost.costo_total) if latest_cost else None
    data['latest_recommended_price'] = to_float(latest_price.precio_recomendado) if latest_price else None
    return ProductResponse(**data)

@router.get('', response_model=list[ProductResponse])
def list_products(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], q: str | None = Query(default=None), include_inactive: bool = False):
    from sqlalchemy.orm import joinedload
    query = select(Product).options(joinedload(Product.proveedor_rel))
    if not include_inactive:
        query = query.where(Product.activo.is_(True))
    if q:
        term = f'%{q.strip()}%'
        query = query.where(or_(Product.nombre.ilike(term), Product.codigo_producto.ilike(term), Product.marca.ilike(term), Product.color.ilike(term), Product.categoria.ilike(term)))
    products = db.scalars(query.order_by(Product.fecha_creacion.desc())).all()
    return [build_product_response(db, product) for product in products]

@router.get('/{product_id}', response_model=ProductResponse)
def get_product(product_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    return build_product_response(db, product)

import uuid

@router.post('', response_model=ProductResponse)
def create_product(payload: ProductCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if not payload.codigo_producto:
        # Autogenerate code
        payload.codigo_producto = f"LAN-{str(uuid.uuid4())[:8].upper()}"

    exists = db.scalar(select(Product).where(Product.codigo_producto == payload.codigo_producto))
    if exists:
        raise HTTPException(status_code=400, detail='Ya existe un producto con ese codigo.')
        
    product_data = payload.model_dump(exclude={'costo_inicial_total', 'compra_incluye_iva'})
    product = Product(**product_data)
    db.add(product)
    db.flush()
    
    # If initial cost is provided, create the cost and calculate price automatically
    if payload.costo_inicial_total is not None and payload.costo_inicial_total > 0:
        settings = db.scalar(select(PriceSetting).limit(1))
        
        # Calculate cost
        costs = calculate_cost_breakdown(
            valor_compra=payload.costo_inicial_total,
            iva_porcentaje=float(settings.iva_porcentaje_default),
            compra_incluye_iva=payload.compra_incluye_iva,
            costos_fijos_generales=float(settings.costos_fijos_generales),
            cantidad=payload.stock if payload.stock > 0 else 1
        )
        
        cost = ProductCost(
            producto_id=product.id,
            valor_compra_neto=costs['valor_compra_neto'],
            iva_porcentaje=costs['iva_porcentaje'],
            valor_iva=costs['valor_iva'],
            valor_compra_bruto=costs['valor_compra_bruto'],
            compra_incluye_iva=payload.compra_incluye_iva,
            costo_total=costs['costo_total']
        )
        db.add(cost)
        
        # Calculate recommended prices based on calculated cost
        pricing = calculate_pricing_from_total(
            costo_total=costs['costo_total'], 
            settings=settings, 
            product=product
        )
        
        calc_price = CalculatedPrice(
            producto_id=product.id,
            costo_total=pricing['costo_total'],
            precio_minimo=pricing['precio_minimo'],
            precio_recomendado=pricing['precio_recomendado'],
            precio_premium=pricing['precio_premium'],
            margen_estimado=pricing['margen_estimado'],
            utilidad_estimada=pricing['utilidad_estimada']
        )
        db.add(calc_price)
        log_change(db, current_user.id, 'product_costs', product.id, 'crear', f'Costo inicial registrado para {product.codigo_producto}.')

    log_change(db, current_user.id, 'products', product.id, 'crear', f'Producto {product.codigo_producto} creado.')
    db.commit()
    db.refresh(product)
    return build_product_response(db, product)

@router.put('/{product_id}', response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    updates = payload.model_dump(exclude_unset=True)
    if 'codigo_producto' in updates:
        exists = db.scalar(select(Product).where(Product.codigo_producto == updates['codigo_producto'], Product.id != product_id))
        if exists:
            raise HTTPException(status_code=400, detail='El codigo de producto ya esta en uso.')
    
    # Check if margins are being updated to trigger price recalculation
    margins_updated = any(k in updates for k in ['margen_minimo_porcentaje', 'margen_recomendado_porcentaje', 'margen_premium_porcentaje'])
    
    for field, value in updates.items():
        setattr(product, field, value)
        
    db.flush() # Ensure product margins are updated in the session
    
    if margins_updated:
        # Recalculate prices if there's a latest cost
        latest_cost = db.scalar(select(ProductCost).where(ProductCost.producto_id == product.id).order_by(ProductCost.fecha_compra.desc(), ProductCost.id.desc()))
        if latest_cost:
            settings = db.scalar(select(PriceSetting).limit(1))
            pricing = calculate_pricing_from_total(
                costo_total=to_float(latest_cost.costo_total), 
                settings=settings, 
                product=product
            )
            calc_price = CalculatedPrice(
                producto_id=product.id,
                costo_total=pricing['costo_total'],
                precio_minimo=pricing['precio_minimo'],
                precio_recomendado=pricing['precio_recomendado'],
                precio_premium=pricing['precio_premium'],
                margen_estimado=pricing['margen_estimado'],
                utilidad_estimada=pricing['utilidad_estimada']
            )
            db.add(calc_price)
            log_change(db, current_user.id, 'calculated_prices', product.id, 'crear', f'Precios recalculados por cambio de márgenes en {product.codigo_producto}.')

    log_change(db, current_user.id, 'products', product.id, 'editar', f'Producto {product.codigo_producto} actualizado.')
    db.commit()
    db.refresh(product)
    return build_product_response(db, product)

@router.delete('/{product_id}', dependencies=[Depends(require_admin)])
def deactivate_product(product_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Producto no encontrado.')
    product.activo = False
    log_change(db, current_user.id, 'products', product.id, 'desactivar', f'Producto {product.codigo_producto} desactivado.')
    db.commit()
    return {'message': 'Producto desactivado correctamente.'}
