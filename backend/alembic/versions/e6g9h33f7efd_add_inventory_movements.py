"""add_inventory_movements

Revision ID: e6g9h33f7efd
Revises: d5f8g22e6dec
Create Date: 2026-06-04 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'e6g9h33f7efd'
down_revision = 'd5f8g22e6dec'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('inventory_movements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('costo_unitario', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('fecha', sa.DateTime(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['producto_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_movements_id'), 'inventory_movements', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_movements_producto_id'), 'inventory_movements', ['producto_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_movements_producto_id'), table_name='inventory_movements')
    op.drop_index(op.f('ix_inventory_movements_id'), table_name='inventory_movements')
    op.drop_table('inventory_movements')
