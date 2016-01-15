import json, csv, datetime

from portal.db import Database, DBSession
from pyramid.view import view_config
from pyramid.renderers import render
from sqlalchemy.ext.hybrid import hybrid_property

from chameleon import PageTemplate
import gns
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy import and_

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
       
# @view_config(route_name='', renderer='json', http_cache=0)
# def api_student_fields(request):
#     pass

@view_config(route_name='api-lastlogins', renderer='json', http_cache=0)
def api_lastlogins(request):
    json_body = request.json_body
    secret = json_body.get('secret')
    if secret != gns.config.api.secret:
        return dict(message="IGBIS api is not for public consumption.", data=[])
    data = []
    with open(gns.config.api.lastloginpath) as f:
        readin = csv.reader(f, delimiter=',')
        for row in readin:
            username = row[0]
            this_date = row[1]
            if this_date == 'lastLoginTime':
                data.append(['Username', 'Lastlogin'])
                continue
            if this_date == 'Never':
                d = 'Never'
            else:
                dte = datetime.datetime.strptime(this_date, '%Y-%m-%dT%H:%M:%S.000Z')
                d = datetime.datetime.strftime(dte, '%A %B %d, %Y @ %I:%M %p')
            data.append([username, d])
    return dict(message="Success", data=data)

@view_config(route_name='api-students', renderer='json', http_cache=0)
def api_students(request):
    json_body = request.json_body
    secret = json_body.get('secret')
    if secret != gns.config.api.secret:
        return dict(message="IGBIS api is not for public consumption.", data=[])
    derived_attr = json_body.get('derived_attr')
    filter = json_body.get('filter')
    awesome_table_filters = json_body.get('awesome_table_filters') or {}
    google_sheets_format = json_body.get('google_sheets_format') or True
    column_map = json_body.get('column_map') or {}
    human_columns = json_body.get('human_columns') or True
    passed_columns = json_body.get('columns') or False

    if derived_attr:
        field_name = derived_attr.get('field')
        string_pattern = derived_attr.get('string')

        # Now use the awesome chameleon to render it as a templating language!
        # TODO: validate the pattern, ensuring that ${things} are in __dict__?
        template = PageTemplate(string_pattern)

        if field_name and string_pattern:
            # Define a new field!
            setattr(Students, field_name, hybrid_property(lambda self_: template.render(**self_.columns_hybrids_dict)))

    if derived_attr:
        columns = [field_name, 'student_id', 'email']
    else:
        columns = []

    if not passed_columns:
        # Add in the extra columns
        column_attrs = Students.columns_and_hybrids()
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
        query = session.query(Students).\
            options(joinedload('parents')).\
            options(joinedload('ib_groups')).\
            options(joinedload_all('classes.teachers')).\
            filter(and_(
                    not Students.is_archived==True,
                    Students.grade != -10,
                    Students.student_id != None
                ))

        if filter == 'filterSecondary':
            query = query.filter(Students.grade >= 6)

        elif filter == 'filterElementary':
            query = query.filter(Students.grade < 6)

        if columns[0] == 'grade_first_nickname_last_studentid':
            query = query.order_by(Students.grade, Students.first_name)
        elif columns[0] == 'grade_last_first_nickname_studentid':
            query = query.order_by(Students.grade, Students.last_name)
        else:
            query = query.order_by(getattr(Students, columns[0]))

        data = query.all()

    #columns = list(Students.__table__.columns.keys())
    # Don't use columns because we have defined stuff at the instance level instead of class level
    # Remove 'id' because we want that at the start

    # insp = inspect(Students)
    # column_attrs = [c.name for c in insp.columns if c.name != 'student_id']
    # column_attrs.extend( [item.__name__ for item in insp.all_orm_descriptors if item.extension_type is HYBRID_PROPERTY and item.__name__ != '<lambda>'] )
    # column_attrs.sort()

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
        ret = [[getattr(data[row], columns[col]) for col in range(len(columns))] for row in range(len(data))]
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
        ret = [[getattr(data[row], columns[col]) for col in range(len(columns))] for row in range(len(data))]
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

