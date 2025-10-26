"""create categories table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(10), nullable=False),
        sa.Column('category_type', sa.Enum('regular', 'shared_cards', 'temporary', name='categorytypeenum'), nullable=False),
        sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('hierarchy_level', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # 인덱스 생성
    op.create_index('idx_categories_user_id', 'categories', ['user_id'])
    op.create_index('idx_categories_parent_id', 'categories', ['parent_id'])

def downgrade() -> None:
    op.drop_table('categories')
