"""add_stock_and_margins

Revision ID: b3d6f00c4bca
Revises: 20260520_0001
Create Date: 2026-06-03 14:12:49.395042
"""
from alembic import op
import sqlalchemy as sa


revision = 'b3d6f00c4bca'
down_revision = '20260520_0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('products', sa.Column('stock', sa.Integer(), server_default='0', nullable=False))
    op.add_column('products', sa.Column('margen_minimo_porcentaje', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('margen_recomendado_porcentaje', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('margen_premium_porcentaje', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('products', 'margen_premium_porcentaje')
    op.drop_column('products', 'margen_recomendado_porcentaje')
    op.drop_column('products', 'margen_minimo_porcentaje')
    op.drop_column('products', 'stock')
