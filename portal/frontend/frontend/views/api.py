import json

from portal.db import Database, DBSession
from pyramid.view import view_config
from pyramid.renderers import render
from sqlalchemy.ext.hybrid import hybrid_property

from chameleon import PageTemplate
import gns
from sqlalchemy.orm import joinedload

db = Database()
Students = db.table_string_to_class('student')

class dummy_first_row:
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
 
    json_body = request.json_body
    secret = json_body.get('secret')
    derived_attr = json_body.get('derived_attr')
    filter = json_body.get('filter')
    awesome_tables = json_body.get('awesome_tables') or False
    human_columns = json_body.get('human_columns') or False
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
        columns = ['student_id', 'email']

    if not passed_columns:
        # Add in the extra columns
        column_attrs = Students.columns_and_hybrids();
        columns.extend([c for c in column_attrs if c not in columns])
    else:
        # Just put in the ones that are requested
        # TODO: Validate, return a useful error
        columns.extend(passed_columns)

    as_multidimentional_arrays = True #'Google-Apps-Script' in request.agent or json_body.get('as_multidimentional_arrays') or 
    data = []
    if secret != gns.config.api.secret:
        return dict(message="IGBIS api is not for public consumption.", data=data)

    with DBSession() as session:

        query = session.query(Students).\
            options(joinedload('parents')).\
            options(joinedload('ib_groups')).\
            options(joinedload_all('classes.teachers')).order_by(Students.first_name)

        if filter == 'filterSecondary':
            query = query.filter(Students.class_year >= 7)  # FIXME class_year is NOT grade!

        elif filter == 'filterElementary':
            query = query.filter(Students.class_year < 7)

        data = query.all()

    #columns = list(Students.__table__.columns.keys())
    # Don't use columns because we have defined stuff at the instance level instead of class level
    # Remove 'id' because we want that at the start

    # insp = inspect(Students)
    # column_attrs = [c.name for c in insp.columns if c.name != 'student_id']
    # column_attrs.extend( [item.__name__ for item in insp.all_orm_descriptors if item.extension_type is HYBRID_PROPERTY and item.__name__ != '<lambda>'] )
    # column_attrs.sort()
 

    if awesome_tables:
        # Add an extra row so that our awesome tables solution works right
        # boo!

        first_row = dummy_first_row()
        filter_map = {'student': 'StringFilter', 'grade': 'CategoryFilter'}
        for column in columns:
            value = filter_map.get(column.lower(), 'NoFilter')
            first_row.add(column, value)

        # insert it into the front
        data.insert(0, first_row)

    if as_multidimentional_arrays:
        ret = [[getattr(data[row], columns[col]) for col in range(len(columns))] for row in range(len(data))]
        if not human_columns:
            columns = [[columns[column] for column in range(len(columns))] for row in range(1)]
        else:
            columns = [[(columns[column]).replace('_', ' ').title() for column in range(len(columns))] for row in range(1)]
        return dict(message="Success, as array", columns=columns, data=ret)
    else:
        if human_columns:
            columns = [c.replace('_', ' ').title() for c in columns]
        return dict(message="Success", columns=columns, data=[d.as_dict() for d in data])