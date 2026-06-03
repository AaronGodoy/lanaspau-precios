from datetime import date
from sqlalchemy import select
from app.db.database import Base, SessionLocal, engine
from app.db.models import Product, ProductCost
from app.services.pricing_service import create_calculated_price
from app.utils.bootstrap import ensure_admin_user, ensure_default_settings

def run() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        settings = ensure_default_settings(db)
        ensure_admin_user(db)
        exists = db.scalar(select(Product).limit(1))
        if exists:
            return
        products = [
            Product(codigo_producto='LANA-001', nombre='Lana Merino Soft', marca='Lanas Pau', categoria='Merino', color='Marfil', gramaje='100 g', metros=180, proveedor='Lanas Pau', descripcion='Ovillo premium para tejidos delicados.'),
            Product(codigo_producto='LANA-002', nombre='Lana Andes Chunky', marca='Lanas Pau', categoria='Chunky', color='Terracota', gramaje='200 g', metros=90, proveedor='Lanas Pau', descripcion='Lana gruesa ideal para mantas y bufandas.'),
            Product(codigo_producto='LANA-003', nombre='Lana Algodon Blend', marca='Lanas Pau', categoria='Blend', color='Azul Petroleo', gramaje='100 g', metros=150, proveedor='Proveedor Alternativo', descripcion='Mezcla suave con buena resistencia.'),
        ]
        db.add_all(products)
        db.commit()
        for index, product in enumerate(products, start=1):
            db.refresh(product)
            base = 4200 + index * 950
            cost = ProductCost(producto_id=product.id, valor_compra_neto=base, iva_porcentaje=19, valor_iva=base * 0.19, valor_compra_bruto=base * 1.19, compra_incluye_iva=False, costo_envio=1200, costo_retiro=500, otros_costos=250, costo_total=base * 1.19 + 1950, fecha_compra=date.today())
            db.add(cost)
            db.flush()
            db.add(create_calculated_price(product.id, float(cost.costo_total), settings))
        db.commit()

if __name__ == '__main__':
    run()
