"""add missing tables

Revision ID: 002
Revises: 001
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('customer_id', UUID(as_uuid=True), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', UUID(as_uuid=True), nullable=False),
        sa.Column('details', JSONB),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Create login_attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('user_agent', sa.String()),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('attempt_time', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('failure_reason', sa.String())
    )

    # Create mfa_settings table
    op.create_table(
        'mfa_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), default=False),
        sa.Column('secret_key', sa.String()),
        sa.Column('backup_codes', ARRAY(sa.String())),
        sa.Column('phone_number', sa.String()),
        sa.Column('email', sa.String()),
        sa.Column('preferred_method', sa.String(), default='totp'),
        sa.Column('last_used', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True))
    )

    # Create password_resets table
    op.create_table(
        'password_resets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String(), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

def downgrade():
    # Drop tables in reverse order
    op.drop_table('password_resets')
    op.drop_table('mfa_settings')
    op.drop_table('login_attempts')
    op.drop_table('audit_logs')
    op.drop_table('tenants') 