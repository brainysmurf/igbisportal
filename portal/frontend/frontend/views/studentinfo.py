import json

from portal.db import Database, DBSession
from pyramid.view import view_config
from pyramid.renderers import render
from sqlalchemy.ext.hybrid import hybrid_property

db = Database()
Students = db.table_string_to_class('student')


# @view_config(route_name='api-students', renderer='json', http_cache=0)
# def student_info()