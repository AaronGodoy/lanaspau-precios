from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), default='usuario')
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cambios: Mapped[list['ChangeHistory']] = relationship(back_populates='usuario')

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo_producto: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    color: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    gramaje: Mapped[str | None] = mapped_column(String(60), nullable=True)
    metros: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    proveedor: Mapped[str] = mapped_column(String(120), default='Lanas Pau')
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    stock: Mapped[int] = mapped_column(default=0)
    stock_minimo: Mapped[int] = mapped_column(default=5)
    margen_minimo_porcentaje: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    margen_recomendado_porcentaje: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    margen_premium_porcentaje: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    costos: Mapped[list['ProductCost']] = relationship(back_populates='producto', cascade='all, delete-orphan')
    precios_calculados: Mapped[list['CalculatedPrice']] = relationship(back_populates='producto', cascade='all, delete-orphan')
    ventas_detalle: Mapped[list['SaleItem']] = relationship(back_populates='producto')

class Sale(Base):
    __tablename__ = 'sales'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fecha_venta: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    items: Mapped[list['SaleItem']] = relationship(back_populates='venta', cascade='all, delete-orphan')
    vendedor: Mapped['User | None'] = relationship()

class SaleItem(Base):
    __tablename__ = 'sale_items'
    __table_args__ = (Index('ix_sale_items_venta_id', 'venta_id'), Index('ix_sale_items_producto_id', 'producto_id'))
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey('sales.id'), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    venta: Mapped['Sale'] = relationship(back_populates='items')
    producto: Mapped['Product'] = relationship(back_populates='ventas_detalle')

class ProductCost(Base):
    __tablename__ = 'product_costs'
    __table_args__ = (Index('ix_product_costs_producto_id', 'producto_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    valor_compra_neto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    iva_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    valor_iva: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    valor_compra_bruto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    compra_incluye_iva: Mapped[bool] = mapped_column(Boolean, default=False)
    costo_envio: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    costo_retiro: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    otros_costos: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    costo_total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_compra: Mapped[date] = mapped_column(Date, default=date.today)
    producto: Mapped['Product'] = relationship(back_populates='costos')

class PriceSetting(Base):
    __tablename__ = 'price_settings'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    margen_minimo_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=20)
    margen_recomendado_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=35)
    margen_premium_porcentaje: Mapped[float] = mapped_column(Numeric(5, 2), default=45)
    iva_porcentaje_default: Mapped[float] = mapped_column(Numeric(5, 2), default=19)
    redondeo_precio: Mapped[str] = mapped_column(String(20), default='100')
    moneda: Mapped[str] = mapped_column(String(10), default='CLP')
    costos_fijos_generales: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

class CalculatedPrice(Base):
    __tablename__ = 'calculated_prices'
    __table_args__ = (Index('ix_calculated_prices_producto_id', 'producto_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    costo_total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_minimo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_recomendado: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_premium: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    margen_estimado: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    utilidad_estimada: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    producto: Mapped['Product'] = relationship(back_populates='precios_calculados')

class ChangeHistory(Base):
    __tablename__ = 'change_history'
    __table_args__ = (Index('ix_change_history_entidad', 'entidad', 'entidad_id'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    entidad: Mapped[str] = mapped_column(String(50), nullable=False)
    entidad_id: Mapped[int] = mapped_column(nullable=False)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usuario: Mapped['User | None'] = relationship(back_populates='cambios')
