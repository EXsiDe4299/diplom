"""Initial migration

Revision ID: 98e6f8fbc3bd
Revises: 
Create Date: 2024-05-03 07:49:46.679984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98e6f8fbc3bd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account_types',
    sa.Column('type_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('type_id')
    )
    op.create_table('database_types',
    sa.Column('type_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('type_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_telegram_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('accounts',
    sa.Column('account_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('account_user_id', sa.Integer(), nullable=False),
    sa.Column('account_login', sa.String(), nullable=False),
    sa.Column('account_password', sa.String(), nullable=False),
    sa.Column('account_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_type_id'], ['account_types.type_id'], ),
    sa.ForeignKeyConstraint(['account_user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    op.create_table('databases',
    sa.Column('database_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('database_name', sa.String(), nullable=False),
    sa.Column('database_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['database_type_id'], ['database_types.type_id'], ),
    sa.PrimaryKeyConstraint('database_id')
    )
    op.create_table('accounts_databases',
    sa.Column('account_database_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('database_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], ),
    sa.ForeignKeyConstraint(['database_id'], ['databases.database_id'], ),
    sa.PrimaryKeyConstraint('account_database_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('accounts_databases')
    op.drop_table('databases')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('database_types')
    op.drop_table('account_types')
    # ### end Alembic commands ###
