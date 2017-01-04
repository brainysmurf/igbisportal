from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from sqlalchemy.sql.expression import text
import gns

database_url = gns.config.database.sqlalchemy_url

@contextmanager
def DBSession():
    session = session_maker()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

engine =  create_engine(database_url, max_overflow=0, pool_size=100, echo=False)
session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

from portal.db.DBInterface import Database
from portal.db.DBModel import Student

metadata = Student.metadata



execute = engine.execute

def get_table_list_from_db():
    """
    return a list of table names from the current
    databases public schema
    """
    sql="select table_name from information_schema.tables "\
        "where table_schema='public'"
    return [name for (name, ) in execute(text(sql))]

def get_seq_list_from_db():
    """return a list of the sequence names from the current
       databases public schema
    """
    sql="select sequence_name from information_schema.sequences "\
        "where sequence_schema='public'"
    return [name for (name, ) in execute(text(sql))]

def drop_all_tables_and_sequences():
    for table in get_table_list_from_db():
        try:
            execute(text("DROP TABLE %s CASCADE" % table))
        except (SQLAlchemyError, e):
            print(e)

    for seq in get_seq_list_from_db():
        try:
            execute(text("DROP SEQUENCE %s CASCADE" % table))
        except (SQLAlchemyError, e):
            print(e)


metadata.create_all(engine)  # creates the database tables and things for us
# TODO: Move this to first_launch

__all__ = [DBSession, Database, session_maker]