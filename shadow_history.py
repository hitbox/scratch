"""
Working out an automatic way of creating shadow tables for sqlalchemy models.
"""
import argparse
import sqlite3

from datetime import datetime
from datetime import timezone
from enum import IntEnum
from time import sleep

import sqlalchemy as sa

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Engine
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TypeDecorator
from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

class Base(DeclarativeBase):
    pass


class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """
        Raise for naive datetime.
        """
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError(
                    f'Expected datetime.datetime, got {type(value)}')
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                raise ValueError(
                    'Naive datetime is not allowed, datetime must be timezone-aware')
        return value

    def process_result_value(self, value, dialect):
        """
        Ensure resulting datetime is timezone aware.
        """
        # Some DBs return naive datetimes even if timezone=True
        if value is not None and value.tzinfo is None:
            # Assume UTC if no tzinfo
            return value.replace(tzinfo=timezone.utc)
        return value


class server_utc_now(expression.FunctionElement):
    """
    Render dialect specific function to get the current UTC time from the
    database.
    """
    # Return type.
    type = DateTime(timezone=True)

    # Mark safe to cache.
    inherit_cache = True


@compiles(server_utc_now, 'postgresql')
def pg_utc_now(element, compiler, **kw):
    return "CURRENT_TIMESTAMP AT TIME ZONE 'UTC'"

@compiles(server_utc_now, 'mysql')
def mysql_utc_now(element, compiler, **kw):
    return 'CURRENT_TIMESTAMP'

@compiles(server_utc_now, 'sqlite')
def sqlite_utc_now(element, compiler, **kw):
    return "(datetime('now'))"

@compiles(server_utc_now)
def default_utc_now(element, compiler, **kw):
    return 'NOW()'

def utc_datetime_column(type_=None, **kwargs):
    if type_ is None:
        type_ = UTCDateTime
    kwargs.setdefault('default', lambda: datetime.now(timezone.utc))
    kwargs.setdefault('server_default', server_utc_now())
    kwargs.setdefault('nullable', False)
    return Column(type_, **kwargs)


# Enum for code-side operations
class OperationTypeEnum(IntEnum):

    INSERT = 1
    UPDATE = 2
    DELETE = 3


# Database table for operation types
class OperationTypeModel(Base):

    __tablename__ = 'operation_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    description = Column(String(100))

    @classmethod
    def get_or_create(cls, session, operation_type: OperationTypeEnum):
        """
        Get or create operation type record
        """
        instance = session.query(cls).filter_by(id=operation_type.value).first()
        if not instance:
            instance = cls(
                id=operation_type.value,
                name=operation_type.name,
                description=f"{operation_type.name.title()} operation"
            )
            session.add(instance)
            session.flush()  # Get the ID without committing
        return instance


class AuditHelper:

    def __init__(self, model_class):
        self.model_class = model_class

    def get_full_history(self, session, record_id, include_operation_details=True):
        """
        Get complete history for a record with operation details
        """
        history_class = self.model_class._history_class
        pk_column = (
            f'{self.model_class.__tablename__}'
            f'_{list(self.model_class.__table__.primary_key.columns)[0].name}'
        )

        query = (
            sa.select(history_class)
            .where(getattr(history_class, pk_column) == record_id)
            .order_by(history_class.operation_timestamp.desc())
        )
        if include_operation_details:
            query = query.join(OperationTypeModel)

        return session.scalars(query).all() #query.all()

    def get_record_at_timestamp(self, session, record_id, timestamp):
        """
        Get the state of a record at a specific timestamp
        """
        history_class = self.model_class._history_class
        pk_column = (
            f'{self.model_class.__tablename__}'
            f'_{list(self.model_class.__table__.primary_key.columns)[0].name}'
        )
        # Get the first history record on or before the given timestamp.
        query = (
            sa.select(history_class)
            .where(
                getattr(history_class, pk_column) == record_id,
                history_class.operation_timestamp <= timestamp,
            )
            .order_by(
                history_class.operation_timestamp.desc(),
            )
        )
        return session.scalars(query).first()

    def get_changes_by_operation(
        self,
        session,
        operation_type,
        start_date = None,
        end_date = None,
    ):
        """
        Get all changes of a specific operation type
        """
        history_class = self.model_class._history_class
        query = (
            sa.select(history_class)
            .where(history_class.operation_type_id == operation_type.value)
        )

        if start_date:
            query = query.where(history_class.operation_timestamp >= start_date)
        if end_date:
            query = query.where(history_class.operation_timestamp <= end_date)

        query = query.order_by(history_class.operation_timestamp.desc())

        return session.scalars(query).all()

    def get_audit_trail(self, session, record_id):
        """
        Get a formatted audit trail for a record
        """
        history_records = self.get_full_history(session, record_id)

        audit_trail = []
        for record in history_records:
            audit_entry = {
                'timestamp': record.operation_timestamp,
                'operation': record.operation_type.name,
                'user': record.operation_user or 'System',
                'changes': {}
            }

            # Add the actual field values
            for column in self.model_class.__table__.columns:
                if not column.primary_key and hasattr(record, column.name):
                    audit_entry['changes'][column.name] = getattr(record, column.name)

            audit_trail.append(audit_entry)

        return audit_trail


class ShadowHistoryMixin:
    """
    Mixin that automatically creates shadow history functionality.
    """

    @classmethod
    def audit(cls):
        return AuditHelper(cls)

    @declared_attr
    def history(cls):
        """
        Relationship to history records
        """
        history_class_name = f'{cls.__name__}History'
        return relationship(
            history_class_name,
            back_populates = cls.__tablename__,
            cascade = 'all, delete-orphan',
            order_by = f'{history_class_name}.operation_timestamp.desc()'
        )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        Automatically create history table when class is defined
        """
        super().__init_subclass__(**kwargs)
        cls._create_history_table()
        cls._setup_event_listeners()

    @classmethod
    def _create_history_table(cls):
        """
        Dynamically create the shadow history table
        """
        history_class_name = f'{cls.__name__}History'
        history_table_name = f'{cls.__tablename__}_history'

        # Build columns dictionary
        new_columns = {
            'history_id': Column(Integer, primary_key=True),
            'operation_type_id': Column(
                Integer,
                ForeignKey('operation_types.id'),
                nullable = False,
            ),
            'operation_timestamp': utc_datetime_column(),
            'operation_user': Column(String(50)),
        }

        for column in cls.__table__.columns:
            if column.primary_key:
                # Create FK back to original PK.
                new_name = f'{cls.__tablename__}_{column.name}'
                new_column = Column(
                    column.type,
                    ForeignKey(
                        column,
                        ondelete = 'SET NULL'
                    ),
                    primary_key = False,
                    autoincrement = False,
                    nullable = True,
                )
                new_columns[new_name] = new_column
            else:
                # Copy regular columns
                new_column = Column(
                    column.type,
                    *column.constraints,
                    nullable = column.nullable,
                )
                new_columns[column.name] = new_column

        # Add relationships
        new_columns['operation_type'] = relationship('OperationTypeModel')
        new_columns[cls.__tablename__] = relationship(
            cls.__name__,
            back_populates = 'history',
            foreign_keys = [
                new_columns[
                    f'{cls.__tablename__}_{cls.__table__.primary_key.columns.keys()[0]}'
                ]
            ],
        )

        # Create the history class
        bases = (
            Base,
        )
        attributes = {
            '__tablename__': history_table_name,
            **new_columns,
        }
        history_class = type(history_class_name, bases, attributes)

        # Store reference for event listeners
        cls._history_class = history_class

        return history_class

    @classmethod
    def _setup_event_listeners(cls):
        """
        Setup automatic history tracking events
        """

        @event.listens_for(cls, 'after_insert')
        def create_insert_history(mapper, connection, target):
            cls._create_history_record(connection, target, OperationTypeEnum.INSERT)

        @event.listens_for(cls, 'after_update')
        def create_update_history(mapper, connection, target):
            cls._create_history_record(connection, target, OperationTypeEnum.UPDATE)

        @event.listens_for(cls, 'after_delete')
        def create_delete_history(mapper, connection, target):
            cls._create_history_record(connection, target, OperationTypeEnum.DELETE)

    @classmethod
    def _create_history_record(cls, connection, target, operation_type: OperationTypeEnum):
        """
        Create a history record
        """
        # Get the primary key value
        pk_column = list(cls.__table__.primary_key.columns)[0]
        pk_value = getattr(target, pk_column.name)

        # Build the history record data
        history_data = {
            f'{cls.__tablename__}_{pk_column.name}': pk_value,
            'operation_type_id': operation_type.value,
            'operation_timestamp': datetime.now(timezone.utc),
        }

        # Copy all non-PK column values
        for column in cls.__table__.columns:
            if not column.primary_key:
                history_data[column.name] = getattr(target, column.name)

        # Insert the history record
        connection.execute(
            cls._history_class.__table__.insert().values(**history_data)
        )


# Example usage with the mixin
class User(ShadowHistoryMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    full_name = Column(String(100))
    created_at = utc_datetime_column()
    # Using Integer for boolean for SQLite compatibility
    is_active = Column(Integer, default=1)


class Product(ShadowHistoryMixin, Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer)  # Price in cents
    description = Column(String(500))
    created_at = Column(
        DateTime(timezone=True),
        server_default = server_utc_now(),
    )


# Context manager for tracking users
@event.listens_for(Engine, 'connect')
def connect(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

def setup_database(engine):
    """
    Initialize the database with required data
    """
    # Create database schema raising for exists.
    Base.metadata.create_all(engine, checkfirst=False)

    # Create operation types
    with Session(engine) as session:
        for op_type in OperationTypeEnum:
            OperationTypeModel.get_or_create(session, op_type)
        session.commit()

def demo(engine):
    with Session(engine) as session:
        # Create and modify a user
        user = User(username='jane_doe', email='jane@example.com', full_name='Jane Doe')
        session.add(user)
        session.commit()

        # Update the user
        user.email = 'jane.doe@newcompany.com'
        user.full_name = 'Jane Smith'
        session.commit()

        # Create a product
        product = Product(name='Widget', price=1999, description='A useful widget')
        session.add(product)
        session.commit()

        # Check the relationships work
        print(f'User has {len(user.history)} history records')
        for hist in user.history:
            print(f'  - {hist.operation_type.name} at {hist.operation_timestamp}')

        # Use query utilities
        audit_trail = User.audit().get_audit_trail(session, user.id)
        print(f'\nAudit trail for user {user.id}:')
        for entry in audit_trail:
            print(f'  {entry['timestamp']}: {entry['operation']} by {entry['user']}')
            for field, value in entry['changes'].items():
                print(f'    {field}: {value}')

def demo(engine):
    with Session(engine) as session:
        # Create and modify a user
        user = User(username='jane_doe', email='jane@example.com', full_name='Jane Doe')
        session.add(user)
        session.commit()
        t1 = datetime.now(timezone.utc)

        # Pause to simulate time gap
        sleep(1)

        # Update the user
        user.email = 'jane.doe@newcompany.com'
        user.full_name = 'Jane Smith'
        session.commit()
        t2 = datetime.now(timezone.utc)

        # Create a product
        product = Product(name='Widget', price=1999, description='A useful widget')
        session.add(product)
        session.commit()

        # Check the relationships work
        print(f'\nUser has {len(user.history)} history records:')
        for hist in user.history:
            print(f'  - {hist.operation_type.name} at {hist.operation_timestamp}')

        # Use audit_trail utility
        audit_trail = User.audit().get_audit_trail(session, user.id)
        print(f'\nAudit trail for user {user.id}:')
        for entry in audit_trail:
            print(f'  {entry["timestamp"]}: {entry["operation"]} by {entry["user"]}')
            for field, value in entry["changes"].items():
                print(f'    {field}: {value}')

        # get_record_at_timestamp
        print(f'\nRecord state at time {t1} (should reflect initial insert):')
        record_at_t1 = User.audit().get_record_at_timestamp(session, user.id, t1)
        if record_at_t1:
            for col in ['username', 'email', 'full_name']:
                print(f'  {col}: {getattr(record_at_t1, col)}')
        else:
            print('  No record found at that time.')

        # get_changes_by_operation
        print(f'\nAll UPDATE operations for User:')
        updates = User.audit().get_changes_by_operation(session, OperationTypeEnum.UPDATE)
        for update in updates:
            print(f'  Update at {update.operation_timestamp}:')
            for col in ['username', 'email', 'full_name']:
                print(f'    {col}: {getattr(update, col)}')

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--echo',
        nargs = '?',
        const = 'enabled', # value for no arguments
        default = 'disabled', # value if not given
    )
    args = parser.parse_args(argv)

    # Setup
    uri = URL.create(
        drivername = 'sqlite',
        database = ':memory:',
    )

    if args.echo == 'disabled':
        echo = False
    elif args.echo == 'enabled':
        echo = True
    else:
        echo = args.echo

    engine = create_engine(uri, echo=echo)
    setup_database(engine)

    demo(engine)

if __name__ == '__main__':
    main()
