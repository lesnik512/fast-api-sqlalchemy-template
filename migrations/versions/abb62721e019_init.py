"""init

Revision ID: abb62721e019
Revises:
Create Date: 2021-05-08 08:24:57.850753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abb62721e019'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('deck',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('card',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('front', sa.String(), nullable=False),
        sa.Column('back', sa.String(), nullable=True),
        sa.Column('hint', sa.String(), nullable=True),
        sa.Column('deck_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['deck_id'], ['deck.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deck_id', 'front', name='card_deck_id_front_uc')
    )


def downgrade():
    op.drop_table('card')
    op.drop_table('deck')
