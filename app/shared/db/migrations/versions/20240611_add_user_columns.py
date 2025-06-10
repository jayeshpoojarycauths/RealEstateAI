"""
Add first_name, last_name, last_login, model_metadata, reset_token, reset_token_expires columns to users table
Remove full_name and role columns from users table

Revision ID: 20240611_add_user_columns
Revises: 
Create Date: 2024-06-11 03:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '20240611_add_user_columns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('model_metadata', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(), nullable=True))
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'role')

def downgrade():
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(), nullable=True))
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'model_metadata')
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'reset_token_expires') 