from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, SessionLocal, engine
from app.modules.auth.router import router as auth_router
from app.modules.costs.router import router as costs_router
from app.modules.pricing.router import router as pricing_router
from app.modules.products.router import router as products_router
from app.modules.reports.router import router as reports_router
from app.modules.settings.router import router as settings_router
from app.modules.users.router import router as users_router
from app.utils.bootstrap import ensure_admin_user, ensure_default_settings

app = FastAPI(title=settings.project_name, version='1.0.0', description='Sistema web para costos, precios de venta e inventario de productos de lana.')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins or ['http://localhost:5173'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_settings(db)
        ensure_admin_user(db)

@app.get('/health')
def health_check() -> dict:
    return {'status': 'ok', 'service': settings.project_name}

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(costs_router, prefix=settings.api_v1_prefix)
app.include_router(pricing_router, prefix=settings.api_v1_prefix)
app.include_router(settings_router, prefix=settings.api_v1_prefix)
app.include_router(reports_router, prefix=settings.api_v1_prefix)
