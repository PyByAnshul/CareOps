"""Add form_type and inquiries

Revision ID: add_form_type_inquiries
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_form_type_inquiries'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add form_type column to forms table
    op.add_column('forms', sa.Column('form_type', sa.String(), nullable=False, server_default='booking'))
    
    # Add inquiry_id column to form_submissions table
    op.add_column('form_submissions', sa.Column('inquiry_id', sa.Integer(), nullable=True))
    
    # Create inquiries table
    op.create_table('inquiries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('form_submission_id', sa.Integer(), nullable=True),
        sa.Column('customer_name', sa.String(), nullable=False),
        sa.Column('customer_email', sa.String(), nullable=False),
        sa.Column('inquiry_type', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['form_submission_id'], ['form_submissions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inquiries_id'), 'inquiries', ['id'], unique=False)
    op.create_index(op.f('ix_inquiries_workspace_id'), 'inquiries', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_inquiries_customer_email'), 'inquiries', ['customer_email'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_inquiries_customer_email'), table_name='inquiries')
    op.drop_index(op.f('ix_inquiries_workspace_id'), table_name='inquiries')
    op.drop_index(op.f('ix_inquiries_id'), table_name='inquiries')
    op.drop_table('inquiries')
    op.drop_column('form_submissions', 'inquiry_id')
    op.drop_column('forms', 'form_type')
