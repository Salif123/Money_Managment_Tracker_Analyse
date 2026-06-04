"""initial

Revision ID: 0001
Revises: 
Create Date: 2026-06-04 19:38:23.748808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categories',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('color', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('vendors',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('gstin', sa.String(), nullable=True),
    sa.Column('pan', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vendors_name'), 'vendors', ['name'], unique=False)
    op.create_table('invoices',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('vendor_id', sa.String(length=36), nullable=True),
    sa.Column('invoice_number', sa.String(), nullable=True),
    sa.Column('invoice_date', sa.Date(), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('discount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('tax_total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('grand_total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.Column('extraction_method', sa.String(), nullable=False),
    sa.Column('raw_text', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice_categories',
    sa.Column('invoice_id', sa.String(length=36), nullable=False),
    sa.Column('category_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('invoice_id', 'category_id')
    )
    op.create_table('line_items',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('invoice_id', sa.String(length=36), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('hsn_code', sa.String(), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=False),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('line_total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('cgst_pct', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('sgst_pct', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('igst_pct', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tax_entries',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('invoice_id', sa.String(length=36), nullable=False),
    sa.Column('tax_type', sa.String(), nullable=False),
    sa.Column('rate', sa.Numeric(precision=5, scale=2), nullable=False),
    sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tax_entries')
    op.drop_table('line_items')
    op.drop_table('invoice_categories')
    op.drop_table('invoices')
    op.drop_index(op.f('ix_vendors_name'), table_name='vendors')
    op.drop_table('vendors')
    op.drop_table('categories')
