"""
Defines the frontend behaviour
"""

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload, joinedload_all

from portal.db import Database, DBSession
db = Database()

import json

import requests

PREFIX = 'igbis2014'
url = 'https://{}.managebac.com/api/{{}}'.format(PREFIX)

api_token = 'a473e92458548d66c06fe83f69831fd5'

Students = db.table_string_to_class('student')
ReportComments = db.table_string_to_class('report_comments')
Courses = db.table_string_to_class('course')

@view_config(route_name='auditlog', renderer='templates/auditlog.pt')
def auditlog(request):
    return dict(project='test')

@view_config(route_name='auditlog_data', renderer='json')
def auditlog_data(request):
    data = {'data':[]}
    for serialized_item in r.smembers('/admin/audit?page={}'):
        python_list = json.loads(serialized_item)
        data['data'].append(python_list)
    return data

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'one': 'yo', 'project': 'frontend'}

@view_config(route_name='grade_course', renderer='templates/grade_course.pt')
def grade_course(request):
    grade = request.params.get('grade')
    if not grade:
        with DBSession() as session:
            statement = session.query(Courses).\
                options(joinedload('students')).\
                options(joinedload('teachers')).\
                options(joinedload('timetables'))

            items = statement.all()

        return dict(title="Grades", rows=items)

    with DBSession() as session:
        statement = session.query(Courses).\
        options(joinedload('students')).\
        options(joinedload('teachers')).\
        options(joinedload('timetables'))

        items = statement.all()


    return dict(title="Grades", rows=items)

@view_config(route_name='grade_course_data', renderer='json')
def grade_course_info(request):

    data = {"data":[]}

    return data

@view_config(route_name='schedule', renderer='templates/schedule.pt')
def schedule(request):
    return dict(api_key='a473e92458548d66c06fe83f69831fd5')

@view_config(route_name='schedule_data', renderer='json')
def schedule_data(request):

    data = {"data":[]}

    for item in db.get_timetable_info():
        data["data"].append(item)

    return data

@view_config(route_name='students', renderer='templates/students.pt')
def students(request):

    with DBSession() as session:
        statement = session.query(Students)
        students = statement.all()

    return dict(title="All Students", items=students)

@view_config(route_name='students_ind', renderer='templates/student.pt')
def students_ind(request):
    m = request.matchdict
    student_id = m.get('id')
    if not student_id:
        return dict(items=[])

    with DBSession() as session:
        statement = session.query(Students).filter(Students.id == student_id)
        student = statement.one()

    return dict(title="Student View", item=student)


@view_config(route_name='splash', renderer='templates/splash.pt')
def splash(request):
    role = request.GET.get('role', 'student')
    return dict(role=role, title="Splash")

@view_config(route_name='reports_ind', renderer='templates/report_ind.pt')
def reports_ind(request):
    m = request.matchdict
    student_id = m.get('id')

    with DBSession() as session:
        statement = session.query(ReportComments).join(Students, Students.id == ReportComments.student_id).\
            options(joinedload(ReportComments.atl_comments)).\
            options(joinedload(ReportComments.course)).\
        filter(Students.id == student_id)
        reports = statement.all()

    return dict(
            title="This person's reports",
            reports=reports
        )


@view_config(route_name='reports', renderer='templates/report_list.pt')
def reports(request):

    db = Database()

    with DBSession() as session:
        statement = session.query(Students).join(ReportComments, ReportComments.student_id == Students.id)
        students_with_report = statement.all()

    return dict(
        student_list=students_with_report,
        title="List of students with reports"
        )

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_frontend_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

