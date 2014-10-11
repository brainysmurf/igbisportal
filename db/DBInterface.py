"""
Construct for providing access to the database and for common operations
The with statements make them transactions
Copied and pasted from something else I wrote, so a lot of these defined methods aren't actually used
TODO: Delete those unused methods
"""

from db import DBSession
from db import DBModel    # yes, import the module itself, used for getattr statements
from db.DBModel import *  # and, yes, import all the terms we need to refer to the tables as classes
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import desc, asc
from sqlalchemy import func, case, Integer, String
from sqlalchemy.dialects.postgres import ARRAY
from sqlalchemy.orm import aliased
from collections import defaultdict
from sqlalchemy.sql.expression import cast

from utils import NS # My way of doing namesapces

import logging
import re

class Database:
    """
    Implements lower-level convenience methods that handles sessions, transactions, queries
    Errors are not trapped, should be handled at higher level
    """
    def __init__(self):
        ns = NS()
        self.logger = logging.getLogger('Database')
        self.default_logger = self.logger.info

    def table_string_to_class(self, table):
        """
        This provides the whole class with an API whereby
        table_name can be a string that equals the equiv in the actual database
        so that places outside of me don't have to do a bunch of imports
        TODO: Find the native sqlalchemy way of doing this conversion
        @table should be a string
        @returns Database class that can be used in queries
        """
        if table.lower().endswith('data'):
            table = table[:-4] + 'datum'
        if table.endswith('s'):
            table = table[:-1]
        ret = getattr(DBModel, table.replace('_', ' ').replace(' ', ''))
        return ret

    def wrap_no_result(self, f, *args, **kwargs):
        """
        For simple work, returns None if NoResultFound is encountered
        Most useful when calling an sqlalchemy function like one() and you want
        a simple way to handle an error
        """
        try:
            return f(*args, **kwargs)
        except NoResultFound:
            return None

    def insert_table(self, table, **kwargs):
        with DBSession() as session:
            table_class = self.table_string_to_class(table)
            instance = table_class()
            for key in kwargs.keys():
                setattr(instance, key, kwargs[key])

            session.add(instance)

    def get_rows_in_table(self, table, **kwargs):
        """
        @table string of the table name (without the prefix)
        @param kwargs is the where statement
        """
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            statement = session.query(table_class).filter_by(**kwargs)
        return statement.all()

    def update_table(self, table, where={}, **kwargs):
        """
        Can only update one row...
        """
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            instance = session.query(table_class).filter_by(**where).one()
            for key in kwargs.keys():
                setattr(instance, key, kwargs[key])
            session.add(instance)

    def get_list_of_attributes(self, table, attr):
        """
        """
        table_class = self.table_string_to_class(table)
        with DBSession() as session:
            instance = session.query(table_class)
        return [getattr(obj, attr) for obj in instance.all()]

    def get_grade_course_info(self, grade=""):
        with DBSession() as session:
            statement = session.query(Course.grade, Course.name, Timetable.day, Timetable.period).\
                select_from(Course).\
                    join(Timetable, Timetable.course_id == Course.id).\
                    filter(Course.grade == grade)
        return statement.all()

    def get_timetable_info(self):
        with DBSession() as session:
            statement = session.query(Student.last_name, Student.first_name, Student.email, Timetable.day, Timetable.period, IBGroup.name, Course.name).\
                select_from(Timetable).\
                    join(Course, Course.id == Timetable.course_id).\
                    join(Enrollment, Enrollment.c.course_id == Course.id).\
                    join(Student, Student.student_id == Enrollment.c.student_id ).\
                    join(IBGroupMembership, IBGroupMembership.c.student_id == Student.student_id).\
                    join(IBGroup, IBGroup.id == IBGroupMembership.c.ib_group_id)
        return statement.all()
