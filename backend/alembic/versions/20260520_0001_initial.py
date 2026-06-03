"""initial schema"""
from alembic import op
import sqlalchemy as sa

revision = '20260520_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users', sa.Column('id', sa.Integer(), nullable=False), sa.Column('nombre', sa.String(length=120), nullable=False), sa.Column('email', sa.String(length=255), nullable=False), sa.Column('password_hash', sa.String(length=255), nullable=False), sa.Column('rol', sa.String(length=20), nullable=False, server_default='usuario'), sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column('fecha_creacion', sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('email'))
    op.create_table('products', sa.Column('id', sa.Integer(), nullable=False), sa.Column('codigo_producto', sa.String(length=50), nullable=False), sa.Column('nombre', sa.String(length=150), nullable=False), sa.Column('marca', sa.String(length=100), nullable=True), sa.Column('categoria', sa.String(length=100), nullable=True), sa.Column('color', sa.String(length=60), nullable=True), sa.Column('gramaje', sa.String(length=60), nullable=True), sa.Column('metros', sa.Numeric(10, 2), nullable=True), sa.Column('proveedor', sa.String(length=120), nullable=False, server_default='Revesderecho'), sa.Column('descripcion', sa.Text(), nullable=True), sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column('fecha_creacion', sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('codigo_producto'))
    op.create_table('price_settings', sa.Column('id', sa.Integer(), nullable=False), sa.Column('margen_minimo_porcentaje', sa.Numeric(5, 2), nullable=False, server_default='20'), sa.Column('margen_recomendado_porcentaje', sa.Numeric(5, 2), nullable=False, server_default='35'), sa.Column('margen_premium_porcentaje', sa.Numeric(5, 2), nullable=False, server_default='45'), sa.Column('iva_porcentaje_default', sa.Numeric(5, 2), nullable=False, server_default='19'), sa.Column('redondeo_precio', sa.String(length=20), nullable=False, server_default='100'), sa.Column('moneda', sa.String(length=10), nullable=False, server_default='CLP'), sa.Column('costos_fijos_generales', sa.Numeric(12, 2), nullable=False, server_default='0'), sa.PrimaryKeyConstraint('id'))
    op.create_table('product_costs', sa.Column('id', sa.Integer(), nullable=False), sa.Column('producto_id', sa.Integer(), nullable=False), sa.Column('valor_compra_neto', sa.Numeric(12, 2), nullable=False), sa.Column('iva_porcentaje', sa.Numeric(5, 2), nullable=False), sa.Column('valor_iva', sa.Numeric(12, 2), nullable=False), sa.Column('valor_compra_bruto', sa.Numeric(12, 2), nullable=False), sa.Column('compra_incluye_iva', sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column('costo_envio', sa.Numeric(12, 2), nullable=False, server_default='0'), sa.Column('costo_retiro', sa.Numeric(12, 2), nullable=False, server_default='0'), sa.Column('otros_costos', sa.Numeric(12, 2), nullable=False, server_default='0'), sa.Column('costo_total', sa.Numeric(12, 2), nullable=False), sa.Column('fecha_compra', sa.Date(), nullable=False), sa.ForeignKeyConstraint(['producto_id'], ['products.id']), sa.PrimaryKeyConstraint('id'))
    op.create_table('calculated_prices', sa.Column('id', sa.Integer(), nullable=False), sa.Column('producto_id', sa.Integer(), nullable=False), sa.Column('costo_total', sa.Numeric(12, 2), nullable=False), sa.Column('precio_minimo', sa.Numeric(12, 2), nullable=False), sa.Column('precio_recomendado', sa.Numeric(12, 2), nullable=False), sa.Column('precio_premium', sa.Numeric(12, 2), nullable=False), sa.Column('margen_estimado', sa.Numeric(5, 2), nullable=False), sa.Column('utilidad_estimada', sa.Numeric(12, 2), nullable=False), sa.Column('fecha_calculo', sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(['producto_id'], ['products.id']), sa.PrimaryKeyConstraint('id'))
    op.create_table('change_history', sa.Column('id', sa.Integer(), nullable=False), sa.Column('usuario_id', sa.Integer(), nullable=True), sa.Column('entidad', sa.String(length=50), nullable=False), sa.Column('entidad_id', sa.Integer(), nullable=False), sa.Column('accion', sa.String(length=50), nullable=False), sa.Column('detalle', sa.Text(), nullable=True), sa.Column('fecha', sa.DateTime(), nullable=False), sa.ForeignKeyConstraint(['usuario_id'], ['users.id']), sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_change_history_entidad', 'change_history', ['entidad', 'entidad_id'])
    op.create_index('ix_product_costs_producto_id', 'product_costs', ['producto_id'])
    op.create_index('ix_calculated_prices_producto_id', 'calculated_prices', ['producto_id'])

def downgrade() -> None:
    op.drop_index('ix_calculated_prices_producto_id', table_name='calculated_prices')
    op.drop_index('ix_product_costs_producto_id', table_name='product_costs')
    op.drop_index('ix_change_history_entidad', table_name='change_history')
    op.drop_table('change_history')
    op.drop_table('calculated_prices')
    op.drop_table('product_costs')
    op.drop_table('price_settings')
    op.drop_table('products')
    op.drop_table('users')
