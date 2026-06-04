"""add sales and stock minimo

Revision ID: c4e7f11d5cdb
Revises: b3d6f00c4bca
Create Date: 2026-06-03 16:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'c4e7f11d5cdb'
down_revision = 'b3d6f00c4bca'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add stock_minimo to products
    op.add_column('products', sa.Column('stock_minimo', sa.Integer(), server_default='5', nullable=False))
    
    # Create sales table
    op.create_table('sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('metodo_pago', sa.String(length=50), nullable=True),
        sa.Column('fecha_venta', sa.DateTime(), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_fecha_venta'), 'sales', ['fecha_venta'], unique=False)
    op.create_index(op.f('ix_sales_id'), 'sales', ['id'], unique=False)

    # Create sale_items table
    op.create_table('sale_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('venta_id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['producto_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['venta_id'], ['sales.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sale_items_id'), 'sale_items', ['id'], unique=False)
    op.create_index(op.f('ix_sale_items_producto_id'), 'sale_items', ['producto_id'], unique=False)
    op.create_index(op.f('ix_sale_items_venta_id'), 'sale_items', ['venta_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_sale_items_venta_id'), table_name='sale_items')
    op.drop_index(op.f('ix_sale_items_producto_id'), table_name='sale_items')
    op.drop_index(op.f('ix_sale_items_id'), table_name='sale_items')
    op.drop_table('sale_items')
    
    op.drop_index(op.f('ix_sales_id'), table_name='sales')
    op.drop_index(op.f('ix_sales_fecha_venta'), table_name='sales')
    op.drop_table('sales')
    
    op.drop_column('products', 'stock_minimo')
