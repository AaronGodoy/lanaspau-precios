import sys
from app.db.database import SessionLocal
from app.db.models import Product, ProductCost, CalculatedPrice, PriceSetting
from app.services.pricing_service import calculate_pricing_from_total
from sqlalchemy import select

db = SessionLocal()
p = db.scalar(select(Product).order_by(Product.id.desc()).limit(1))
if not p:
    print('No products')
    sys.exit(0)

print(f"Product: {p.nombre}")
print(f"Margins: min={p.margen_minimo_porcentaje}, rec={p.margen_recomendado_porcentaje}, prem={p.margen_premium_porcentaje}")

latest_cost = db.scalar(select(ProductCost).where(ProductCost.producto_id == p.id).order_by(ProductCost.id.desc()))
latest_price = db.scalar(select(CalculatedPrice).where(CalculatedPrice.producto_id == p.id).order_by(CalculatedPrice.id.desc()))

if latest_cost:
    print(f"Latest Cost Total: {latest_cost.costo_total}")
    settings = db.scalar(select(PriceSetting).limit(1))
    pricing = calculate_pricing_from_total(latest_cost.costo_total, settings, product=p)
    print(f"Calculated Pricing from total: {pricing}")
else:
    print("No latest cost")

if latest_price:
    print(f"Price in DB: min={latest_price.precio_minimo}, rec={latest_price.precio_recomendado}, prem={latest_price.precio_premium}")
    print(f"Est Margin in DB: {latest_price.margen_estimado}")
else:
    print('No price')
