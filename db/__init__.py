from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# ns = NS2()
# ns.db_username = config['MOODLE'].get('db_username')
# ns.db_prefix = config['MOODLE'].get('db_prefix')
# ns.db_password = config['MOODLE'].get('db_password')
# ns.db_host = config['MOODLE'].get('db_host')
# ns.db_name = config['MOODLE'].get('db_name')

engine =  create_engine(
    # 'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'.\
    #     format(**ns.declared_kwargs),
    'postgresql://igbisportaluser:igbisportaluser@localhost/igbisportal',
        max_overflow=0, pool_size=100, echo=False)
session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

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

from db.DBInterface import Database

from db.DBModel import Student, Parent, Advisor

Student.metadata.create_all(engine)
#Advisor.metadata.create_all(engine)
#Parent.metadata.create_all(engine)

__all__ = [DBSession, Database]

