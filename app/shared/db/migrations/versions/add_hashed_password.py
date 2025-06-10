"""add hashed_password column

Revision ID: add_hashed_password
Revises: 
Create Date: 2024-06-11 02:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_hashed_password'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add hashed_password column
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    
    # Update existing users with a default hashed password
    # This is just a placeholder - you should update this with proper password hashing
    op.execute("UPDATE users SET hashed_password = 'placeholder' WHERE hashed_password IS NULL")
    
    # Make the column non-nullable after setting default values
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=False)

def downgrade():
    op.drop_column('users', 'hashed_password') 