from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.database.sqlite_database import SqliteBase


class AccountDatabase(SqliteBase):
    __tablename__ = 'accounts_databases'

    account_database_id = Column('account_database_id', Integer(), primary_key=True, autoincrement=True)
    database_id = Column('database_id', Integer(), ForeignKey('databases.database_id'), nullable=False)
    account_id = Column('account_id', Integer(), ForeignKey('accounts.account_id'), nullable=False)

    databases = relationship('Database')
    accounts = relationship('Account')


class Account(SqliteBase):
    __tablename__ = 'accounts'

    account_id = Column('account_id', Integer(), primary_key=True, autoincrement=True)
    account_user_id = Column('account_user_id', Integer(), ForeignKey('users.user_id'), nullable=False)
    account_login = Column('account_login', String(), nullable=False)
    account_password = Column('account_password', String(), nullable=False)
    account_type_id = Column('account_type_id', Integer(), ForeignKey('account_types.type_id'), nullable=False)

    users = relationship('User')
    account_types = relationship('AccountTypes')


class User(SqliteBase):
    __tablename__ = 'users'

    user_id = Column('user_id', Integer(), primary_key=True, autoincrement=True)
    user_telegram_id = Column('user_telegram_id', String(), nullable=False)


class AccountTypes(SqliteBase):
    __tablename__ = 'account_types'

    type_id = Column('type_id', Integer(), primary_key=True, autoincrement=True)
    type_name = Column('type_name', String(), nullable=False)


class Database(SqliteBase):
    __tablename__ = 'databases'

    database_id = Column('database_id', Integer(), primary_key=True, autoincrement=True)
    database_name = Column('database_name', String(), nullable=False)
    database_type_id = Column('database_type_id', Integer(), ForeignKey('database_types.type_id'), nullable=False)

    database_types = relationship('DatabaseTypes')


class DatabaseTypes(SqliteBase):
    __tablename__ = 'database_types'

    type_id = Column('type_id', Integer(), primary_key=True, autoincrement=True)
    type_name = Column('type_name', String(), nullable=False)
