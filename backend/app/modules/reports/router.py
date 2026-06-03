from typing import Annotated, Callable
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.services.report_service import build_inventory_rows, build_pricing_history_rows, build_product_rows, rows_to_csv, rows_to_xlsx

router = APIRouter(prefix='/reports', tags=['Reportes'])

def make_export(rows: list[dict], format_: str, filename: str, sheet_name: str) -> StreamingResponse:
    if format_ == 'xlsx':
        content = rows_to_xlsx(rows, sheet_name)
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'
    else:
        content = rows_to_csv(rows)
        media_type = 'text/csv'
        extension = 'csv'
    headers = {'Content-Disposition': f'attachment; filename={filename}.{extension}'}
    return StreamingResponse(iter([content]), media_type=media_type, headers=headers)

def export_report(builder: Callable[[Session], list[dict]], filename: str, sheet_name: str, format_: str, db: Session) -> StreamingResponse:
    return make_export(builder(db), format_, filename, sheet_name)

@router.get('/products')
def export_products(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], format_: str = Query(default='csv', alias='format', pattern='^(csv|xlsx)$')):
    return export_report(build_product_rows, 'productos', 'Productos', format_, db)

@router.get('/pricing-history')
def export_pricing_history(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], format_: str = Query(default='csv', alias='format', pattern='^(csv|xlsx)$')):
    return export_report(build_pricing_history_rows, 'historial_precios', 'Historial', format_, db)

@router.get('/inventory')
def export_inventory(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], format_: str = Query(default='csv', alias='format', pattern='^(csv|xlsx)$')):
    return export_report(build_inventory_rows, 'inventario_valorizado', 'Inventario', format_, db)
