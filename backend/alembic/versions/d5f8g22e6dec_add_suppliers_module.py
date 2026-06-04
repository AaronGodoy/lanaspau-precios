"""add suppliers module

Revision ID: d5f8g22e6dec
Revises: c4e7f11d5cdb
Create Date: 2026-06-03 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'd5f8g22e6dec'
down_revision = 'c4e7f11d5cdb'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create suppliers table
    op.create_table('suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('contacto', sa.String(length=150), nullable=True),
        sa.Column('telefono', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('direccion', sa.Text(), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_suppliers_nombre'), 'suppliers', ['nombre'], unique=False)

    # 2. Add proveedor_id to products
    op.add_column('products', sa.Column('proveedor_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_products_proveedor_id', 'products', 'suppliers', ['proveedor_id'], ['id'])
    
    # 3. Drop legacy string column
    op.drop_column('products', 'proveedor')

def downgrade() -> None:
    op.add_column('products', sa.Column('proveedor', sa.String(length=120), server_default='Lanas Pau', nullable=False))
    op.drop_constraint('fk_products_proveedor_id', 'products', type_='foreignkey')
    op.drop_column('products', 'proveedor_id')
    
    op.drop_index(op.f('ix_suppliers_nombre'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_id'), table_name='suppliers')
    op.drop_table('suppliers')
