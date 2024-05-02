from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.database.sqlite_database import SqliteBase


class AccountDatabase(SqliteBase):
    __tablename__ = 'accounts_databases'

    user_database_id = Column('account_database_id', Integer(), primary_key=True, autoincrement=True)
    account_id = Column('account_id', Integer(), ForeignKey('accounts.account_id'), nullable=False)
    database_id = Column('database_id', Integer(), ForeignKey('databases.database_id'), nullable=False)


class Account(SqliteBase):
    __tablename__ = 'accounts'

    account_id = Column('account_id', Integer(), primary_key=True, autoincrement=True)
    user_id = Column('user_id', String(), ForeignKey('users.user_telegram_id'), nullable=False)
    account_type_id = Column(Integer, ForeignKey('account_types.type_id'), nullable=False)


class User(SqliteBase):
    __tablename__ = 'users'

    user_telegram_id = Column(String, primary_key=True)
    user_login = Column(String, nullable=False)
    user_password = Column(String, nullable=False)

    databases = relationship('Database', secondary='users_databases', back_populates='users')


class AccountTypes(SqliteBase):
    __tablename__ = 'account_types'

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String, nullable=False)

    accounts = relationship('Account')


class Database(SqliteBase):
    __tablename__ = 'databases'

    database_id = Column(Integer, primary_key=True, autoincrement=True)
    database_name = Column(String, nullable=False)

    database_type_id = Column(Integer, ForeignKey('database_types.type_id'), nullable=False)

    users = relationship('User', secondary='users_databases', back_populates='databases')


class DatabaseTypes(SqliteBase):
    __tablename__ = 'database_types'

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String, nullable=False)

    databases = relationship('Database')
