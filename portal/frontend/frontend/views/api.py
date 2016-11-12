import json, csv, datetime

from portal.db import Database, DBSession
from pyramid.view import view_config
from pyramid.renderers import render
from sqlalchemy.ext.hybrid import hybrid_property

from chameleon import PageTemplate
import gns
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy import and_, or_

db = Database()
Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')

class dummy_row:
    """
    Terrible. No good day I am having
    """
    def __init__(self):
        self._columns = []

    def add(self, column, value):
        self._columns.append(column)
        setattr(self, column, value)

    def as_dict(self):
       return {c: getattr(self, c) for c in self._columns}

@view_config(route_name='api-students', renderer='json', http_cache=0)
def api_students(request):
    try:
        json_body = request.json_body
    except ValueError:
        return dict(message="Expecting json body")
    secret = json_body.get('secret')
    if secret != gns.config.api.secret:
        return dict(message="IGBIS api is not for public consumption.", data=[])
    derived_attr = json_body.get('derived_attr')
    filter_by = json_body.get('filter_by')
    if filter_by:
        try:
            filter_by = getattr(Student, filter_by)
        except AttributeError:
            filter_by = None
    awesome_table_filters = json_body.get('awesome_table_filters') or {}
    google_sheets_format = json_body.get('google_sheets_format') or True
    column_map = json_body.get('column_map') or {}
    human_columns = json_body.get('human_columns') or True
    columns = json_body.get('columns') or []
    order_by_column = json_body.get('order_by') or None
    every_column = json_body.get('every_column') or False
    if every_column:
        column_attrs = Students.columns_and_hybrids()
        columns.extend([c for c in column_attrs if c not in columns])

    google_sheets_format = True #'Google-Apps-Script' in request.agent or json_body.get('google_sheets_format') or 
    data = []

    with DBSession() as session:

        # TODO: Make database function that allows for filtering out students who
        # are both enrolled and fall within the start date

        query = session.query(Students).\
            options(joinedload('parents')).\
            options(joinedload('ib_groups')).\
            options(joinedload_all('classes.teachers')).\
            options(joinedload('homeroom_teacher')).\
            filter(and_(
                    Students.is_archived==False,
                    Students.grade != -10,
                    Students.student_id != None,
                    Students.status == 'enrolled'
                ))

        if order_by_column:
            query = query.order_by(getattr(Students, order_by_column))

        else:
            # We want to automatically sort by the first column: 
            #    exception: if the first column startswith "grade", in which case we want to sort by integer grade rather than string grade
            if columns and columns[0].startswith('grade_'):
                query = query.order_by(Students.grade, Students.first_name)
            else:
                query = query.order_by(getattr(Students, columns[0]))

        data = query.all()

    if awesome_table_filters:
        # Add an extra row so that our awesome tables solution works right

        second_row = dummy_row()
        for column in columns:
            value = awesome_table_filters.get(column.lower(), 'NoFilter')
            second_row.add(column, value)
        # insert it into the front
        data.insert(0, second_row)

    if google_sheets_format:

        # FIXME: This takes up to 9 seconds...
        ret = []
        for row in range(len(data)):
            r = []
            for col in columns:
                v = getattr(data[row], col, "")
                if v is None:
                    v = ""
                r.append(v)
            ret.append(r)
        #ret = [[getattr(data[row], columns[col], "") for col in range(len(columns))] for row in range(len(data))]

        if not human_columns:
            columns = [[column_map.get(columns[column]) or columns[column] for column in range(len(columns))] for row in range(1)]
        else:
            columns = [[column_map.get(columns[column]).replace('_', '').title() if column_map.get(columns[column]) else columns[column].replace('_', ' ').title() for column in range(len(columns))] for row in range(1)]

        return dict(message="Success, as array", columns=columns, data=ret)
    else:
        if human_columns:
            columns = [c.replace('_', ' ').title() for c in columns]
        else:
            columns = [column_map.get(c) for c in columns]
        return dict(message="Success", columns=columns, data=[d.as_dict() for d in data])

@view_config(route_name='api-teachers', renderer='json', http_cache=0)
def api_teachers(request):
    json_body = request.json_body
    secret = json_body.get('secret')
    if secret != gns.config.api.secret:
        return dict(message="IGBIS api is not for public consumption.", data=[])
    awesome_table_filters = json_body.get('awesome_table_filters') or {}
    google_sheets_format = json_body.get('google_sheets_format') or True
    column_map = json_body.get('column_map') or {}
    human_columns = json_body.get('human_columns') or True
    passed_columns = json_body.get('columns') or False

    columns = []

    if not passed_columns:
        # Add in the extra columns
        column_attrs = Teachers.columns_and_hybrids();
        columns.extend([c for c in column_attrs if c not in columns])
    else:
        # Just put in the ones that are requested
        # TODO: Validate, return a useful error
        columns.extend(passed_columns)

    google_sheets_format = True #'Google-Apps-Script' in request.agent or json_body.get('google_sheets_format') or 
    data = []

    with DBSession() as session:

        # TODO: Make database function that allows for filtering out students who
        # are both enrolled and fall within the start date
        query = session.query(Teachers).\
            options(joinedload('classes')).\
            order_by(Teachers.first_name)

        if filter == 'filterSecondary':
            query = query.filter(Teachers.grade >= 7)

        elif filter == 'filterElementary':
            query = query.filter(Teachers.grade < 7)

        data = query.all()

    if awesome_table_filters:
        # Add an extra row so that our awesome tables solution works right
        # boo!

        second_row = dummy_row()
        for column in columns:
            value = awesome_table_filters.get(column.lower(), 'NoFilter')
            second_row.add(column, value)
        # insert it into the front
        data.insert(0, second_row)

    if google_sheets_format:

        # FIXME: Turn the 
        ret = []
        for row in range(len(data)):
            r = []
            for col in columns:
                v = getattr(data[row], columns[col], "")
                if v is None:
                    v = ""
                r.append(v)
            ret.append(r)
        #ret = [[getattr(data[row], columns[col]) for col in range(len(columns))] for row in range(len(data))]

        if not human_columns:
            columns = [[column_map.get(columns[column]) or columns[column] for column in range(len(columns))] for row in range(1)]
        else:
            columns = [[column_map.get(columns[column]).replace('_', '').title() if column_map.get(columns[column]) else columns[column].replace('_', ' ').title() for column in range(len(columns))] for row in range(1)]
        return dict(message="Success, as array", columns=columns, data=ret)
    else:
        if human_columns:
            columns = [c.replace('_', ' ').title() for c in columns]
        else:
            columns = [column_map.get(c) for c in columns]
        return dict(message="Success", columns=columns, data=[d.as_dict() for d in data])

@view_config(route_name='api-family-info', renderer='json', http_cache=0)
def api_family_info(request):

    json_body = request.json_body
    secret = json_body.get('secret')
    if secret != gns.config.api.secret:
        return dict(message="IGBIS api is not for public consumption.", data=[])

    from cli.parent_accounts import ParentAccounts
    parents = ParentAccounts()
    ret = []
    columns = [['email_address', 'family_id']]
    for family in parents.family_accounts:
        for student in family.students:
            ret.append((student.email, family.family_id))
        for parent in family.parents:
            ret.append((parent.igbis_email_address, family.family_id))
    return dict(message="Success", columns=columns, data=ret)
