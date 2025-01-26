"""Adiciona campo config na tabela sources

Revision ID: add_source_config
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Adiciona a coluna config como JSON
    op.add_column('sources', sa.Column('config', sa.JSON(), nullable=True))

def downgrade():
    # Remove a coluna config
    op.drop_column('sources', 'config')
