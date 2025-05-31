"""Change CommunicationPreferences ID fields to UUID

Revision ID: 001
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create temporary UUID columns
    op.add_column('communication_preferences', sa.Column('new_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('communication_preferences', sa.Column('new_customer_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Generate UUIDs for existing rows
    op.execute("""
        UPDATE communication_preferences 
        SET new_id = gen_random_uuid(),
            new_customer_id = customers.id::uuid
        FROM customers 
        WHERE communication_preferences.customer_id = customers.id
    """)
    
    # Drop foreign key constraints
    op.drop_constraint('communication_preferences_customer_id_fkey', 'communication_preferences', type_='foreignkey')
    
    # Drop old columns and rename new ones
    op.drop_column('communication_preferences', 'id')
    op.drop_column('communication_preferences', 'customer_id')
    op.alter_column('communication_preferences', 'new_id', new_column_name='id')
    op.alter_column('communication_preferences', 'new_customer_id', new_column_name='customer_id')
    
    # Add primary key and foreign key constraints
    op.alter_column('communication_preferences', 'id', nullable=False)
    op.alter_column('communication_preferences', 'customer_id', nullable=False)
    op.create_primary_key('communication_preferences_pkey', 'communication_preferences', ['id'])
    op.create_foreign_key(
        'communication_preferences_customer_id_fkey',
        'communication_preferences', 'customers',
        ['customer_id'], ['id']
    )

def downgrade():
    # Create temporary integer columns
    op.add_column('communication_preferences', sa.Column('old_id', sa.Integer(), nullable=True))
    op.add_column('communication_preferences', sa.Column('old_customer_id', sa.Integer(), nullable=True))
    
    # Convert UUIDs back to integers (this will fail if UUIDs don't map to integers)
    op.execute("""
        UPDATE communication_preferences 
        SET old_id = id::text::integer,
            old_customer_id = customer_id::text::integer
    """)
    
    # Drop foreign key constraints
    op.drop_constraint('communication_preferences_customer_id_fkey', 'communication_preferences', type_='foreignkey')
    
    # Drop UUID columns and rename integer columns
    op.drop_column('communication_preferences', 'id')
    op.drop_column('communication_preferences', 'customer_id')
    op.alter_column('communication_preferences', 'old_id', new_column_name='id')
    op.alter_column('communication_preferences', 'old_customer_id', new_column_name='customer_id')
    
    # Add primary key and foreign key constraints
    op.alter_column('communication_preferences', 'id', nullable=False)
    op.alter_column('communication_preferences', 'customer_id', nullable=False)
    op.create_primary_key('communication_preferences_pkey', 'communication_preferences', ['id'])
    op.create_foreign_key(
        'communication_preferences_customer_id_fkey',
        'communication_preferences', 'customers',
        ['customer_id'], ['id']
    ) 