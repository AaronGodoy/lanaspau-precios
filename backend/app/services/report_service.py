import csv
from io import BytesIO, StringIO
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import CalculatedPrice, Product, ProductCost
from app.services.pricing_service import to_float


def latest_cost_for(db: Session, product_id: int) -> ProductCost | None:
    return db.scalar(select(ProductCost).where(ProductCost.producto_id == product_id).order_by(ProductCost.fecha_compra.desc(), ProductCost.id.desc()))


def latest_price_for(db: Session, product_id: int) -> CalculatedPrice | None:
    return db.scalar(select(CalculatedPrice).where(CalculatedPrice.producto_id == product_id).order_by(CalculatedPrice.fecha_calculo.desc(), CalculatedPrice.id.desc()))


def build_product_rows(db: Session) -> list[dict]:
    rows = []
    products = db.scalars(select(Product).order_by(Product.fecha_creacion.desc())).all()
    for product in products:
        latest_cost = latest_cost_for(db, product.id)
        latest_price = latest_price_for(db, product.id)
        rows.append({'codigo_producto': product.codigo_producto, 'nombre': product.nombre, 'marca': product.marca or '', 'categoria': product.categoria or '', 'color': product.color or '', 'proveedor': product.proveedor, 'activo': 'Si' if product.activo else 'No', 'costo_total': to_float(latest_cost.costo_total) if latest_cost else 0, 'precio_recomendado': to_float(latest_price.precio_recomendado) if latest_price else 0, 'margen_estimado': to_float(latest_price.margen_estimado) if latest_price else 0})
    return rows


def build_pricing_history_rows(db: Session) -> list[dict]:
    rows = []
    products = {product.id: product for product in db.scalars(select(Product)).all()}
    price_history = db.scalars(select(CalculatedPrice).order_by(CalculatedPrice.fecha_calculo.desc())).all()
    for price in price_history:
        product = products.get(price.producto_id)
        rows.append({'codigo_producto': product.codigo_producto if product else '', 'nombre': product.nombre if product else '', 'costo_total': to_float(price.costo_total), 'precio_minimo': to_float(price.precio_minimo), 'precio_recomendado': to_float(price.precio_recomendado), 'precio_premium': to_float(price.precio_premium), 'margen_estimado': to_float(price.margen_estimado), 'utilidad_estimada': to_float(price.utilidad_estimada), 'fecha_calculo': price.fecha_calculo.isoformat()})
    return rows


def build_inventory_rows(db: Session) -> list[dict]:
    rows = []
    products = db.scalars(select(Product).order_by(Product.nombre.asc())).all()
    for product in products:
        latest_cost = latest_cost_for(db, product.id)
        latest_price = latest_price_for(db, product.id)
        rows.append({'codigo_producto': product.codigo_producto, 'nombre': product.nombre, 'categoria': product.categoria or '', 'proveedor': product.proveedor, 'costo_invertido': to_float(latest_cost.costo_total) if latest_cost else 0, 'valor_potencial_venta': to_float(latest_price.precio_recomendado) if latest_price else 0})
    return rows


def rows_to_csv(rows: list[dict]) -> bytes:
    output = StringIO()
    if not rows:
        output.write('sin_datos\\n')
        return output.getvalue().encode('utf-8-sig')
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8-sig')


def rows_to_xlsx(rows: list[dict], sheet_name: str) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    if rows:
        headers = list(rows[0].keys())
        sheet.append(headers)
        for row in rows:
            sheet.append([row.get(key, '') for key in headers])
    else:
        sheet.append(['sin_datos'])
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer.read()
