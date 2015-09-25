# -*- coding: utf-8 -*-

"""
Defines the frontend behaviour
"""

from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.renderers import render

from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy import inspect

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.functions import concat
from sqlalchemy.ext.hybrid import hybrid_property

from chameleon import PageTemplate

from portal.db import Database, DBSession
db = Database()

import json, re, uuid
from collections import defaultdict

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import requests
from sqlalchemy import func

from collections import namedtuple, OrderedDict

import gns

class ReportIncomplete(Exception):
    def __init__(self, msg):
        self.msg = msg

Students = db.table_string_to_class('student')
Parents = db.table_string_to_class('parent')
Teachers = db.table_string_to_class('advisor')
BusAdmin = db.table_string_to_class('BusAdmin')
Users = db.table_string_to_class('users')
Enrollments = db.table_string_to_class('enrollment')
Assignments = db.table_string_to_class('assignment')
ReportComments = db.table_string_to_class('report_comments')
PrimaryReport = db.table_string_to_class('primary_report')
Courses = db.table_string_to_class('course')
Absences = db.table_string_to_class('PrimaryStudentAbsences')
HRTeachers = db.table_string_to_class('secondary_homeroom_teachers')
GSignIn = db.table_string_to_class('google_sign_in')
UserSettings = db.table_string_to_class('user_settings')

@view_config(route_name="get_session_user", renderer="json")
def get_session_user(request):
    return request.session.get('mb_user')

@view_config(route_name="session_user", renderer="json")
def session_user(request):
    """
    Converts the credentials to a database user
    """
    if 'mb_user' in request.session and request.session['mb_user']:
        return dict(message="Already got user!")

    if not hasattr(request, 'session') or 'credentials' not in request.session:
        return dict(message="session_user called before session info, you need to use signinCallback (or equiv code) first")

    credentials = request.session['credentials']
    unique_id = credentials.id_token['sub']
    user_email = credentials.id_token.get('email', '').lower()

    access_token = credentials.access_token

    if not user_email:
        return dict(message="Error: No user email detected?\n{}".format(str(credentials.id_token)))

    user = None

    with DBSession() as session:
        student = session.query(Students).filter(func.lower(Students.email)==user_email).options(joinedload('classes')).first()
        if student:
            user = student
        if not user:
            teacher = session.query(Teachers).filter(func.lower(Teachers.email)==user_email).options(joinedload('classes')).first()
            if teacher:
                user = teacher
        if not user:
            busadmin = session.query(BusAdmin).filter(func.lower(BusAdmin.email)==user_email).first()
            if busadmin:
                user = busadmin
        if not user:
            parent = session.query(Parents).filter(func.lower(Parents.igbis_email_address)==user_email).first()
            if parent:
                user = parent

        if not user: # authenticated, but not in MB, so just put in users table

            gl_user = session.query(Users).filter(func.lower(Users.email) == user_email.lower()).first()

            if not gl_user:

                new_user = Users(email=user_email, igbid=0)
                # TODO: This isn't the best way to get the name info...
                # Can use scope userinfo.profile
                handle = re.sub('@.*', '', user_email)
                if '.' in handle:
                    hsplit = handle.split('.')
                    if len(hsplit) == 2:
                        new_user.first_name, new_user.last_name = [h.title() for h in hsplit]
                    elif len(hsplit) > 2:
                        first, extra, last = [h.title() for h in handle.split('.')]
                    else:
                        new_user.first_name = handle
                        new_user.last_name = ""
                else:
                    new_user.first_name, new_user.last_name = ['*Unknown*', 'Name']
                new_user.type = "Other"

                new_user.g_plus_unique_id = unique_id
                request.session['mb_user'] = None
                request.session['gl_user'] = user
                unique_id = credentials.id_token['sub']
                request.session['g_plus_unique_id'] = unique_id

                session.add(new_user)

            else:
                request.session['mb_user'] = None
                request.session['gl_user'] = gl_user


        else:  # found within managebac

            # Updates the g_plus_unique_id, since it's inside a transaction
            if user.g_plus_unique_id != unique_id:
                user.g_plus_unique_id = unique_id
                # ... most commonly this happens upon first login
                # ... so it should be possible to see that someone has logged in for the first time 
                # ... by checking

            request.session['mb_user'] = user
            request.session['gl_user'] = None
            request.session['g_plus_unique_id'] = unique_id

    return dict(message="User found on ManageBac")

def credentials_flow(request, code):
    try:
        oauth_flow = \
            flow_from_clientsecrets(
                gns('{config.paths.frontend_home}/client_secret.json'), 
                scope="",
                redirect_uri='postmessage'
            )
        oauth_flow.redirect_uris = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return dict(message="Failed to upgrade the authorization code.")

    # Ask Google for info
    access_token = credentials.access_token
    result = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))

    if result.ok:
        # No need:
        # http://stackoverflow.com/questions/16747986/checking-the-user-id-in-a-tokeninfo-response-with-token-received-from-the-googl
        # if result.json()['user_id'] != gplus_id:
        #     return dict(message="Token's user ID doesn't match given ID")

        result_json = result.json()

        if 'issued_to' in result_json:
            if result_json['issued_to'] != gns.config.google.client_id:
                return dict(message='Token does not match application')
        else:
            print('no issued_to in result after API call??')

        stored_credentials = request.session.get('credentials')

        if stored_credentials is not None:
            return dict(message="Current user is already connected")

        request.session['credentials'] = credentials
        unique_id = credentials.id_token['sub']  # guaranteed to exist and to be unique

        with DBSession() as session:
            try:
                exists = session.query(GSignIn).filter_by(unique_id=unique_id).one()
                if exists:
                    # update it!
                    if exists.access_token != credentials.access_token:
                        exists.access_token = credentials.access_token
                    if exists.refresh_token != credentials.refresh_token:
                        exists.refresh_token = credentials.refresh_token

            except NoResultFound:
                sign_in = GSignIn(
                    unique_id=credentials.id_token['sub'],  # always unique
                    auth_code=code,
                    access_token=credentials.access_token,
                    refresh_token=credentials.refresh_token,
                )
                session.add(sign_in)

        return HTTPFound(location="session_user")

    elif result.status_code == 403:
        return dict(message="Forbidden: {}".format(result.status_code))
    else:
       return dict(message="Error: {}".format(result.status_code))    

@view_config(route_name="signinCallback", renderer="json")
def signinCallback(request):
    """
    Does token checking and puts credentials in the session
    """

    try:
        unique = request.params.keys()[0]
    except KeyError:
        return dict(message="error, identifier not passed!")

    try:
        session_unique = request.session['unique_id']
    except KeyError:
        return dict(message="no unique_id?")

    if unique == session_unique:

        auth_object = request.json['authResult']
        code = request.json['code']

        if auth_object['status']['signed_in']:

            if request.session.get('mb_user'):
                return dict(message="User already in session! Woohoo!")

            if request.session.get('credentials'):
                return HTTPFound(location="session_user")
            
            return credentials_flow(request, code) 

        return credentials_flow(request, code)

    return dict(message="Uniques don't match, which happens on reloads")


# @view_config(route_name="gd_starred", renderer='json')
# def gd_starred(request):
#     pass

@view_config(route_name="mb_grade_teachers", renderer="json")
def mb_grade_teachers(request):
    user = request.session.get('mb_user')
    if not user:
        return dict(message="No user in session?", data=[])
    if user.type != 'Advisors':
        return dict(message="Not a teacher", data=[])

    raw_data = defaultdict(list)
    with DBSession() as session:
        records = session.query(Teachers).options(joinedload('classes')).all()
        for record in records:
            for course in record.classes:
                g = re.sub('[^0-9]', '', course.grade)
                if not g:
                    continue
                grade = int(g)
                if grade < 6:
                    continue
                if record.email.startswith('superadmin'):
                    continue
                if record.email.startswith('abena'):
                    continue
                raw_data[grade].append(record.email)

    data = []
    # Convert keys to integers, and sort by that
    for grade in raw_data:
        teacher_emails = ",".join(set(raw_data[grade]))
        data.append(dict(grade=grade, teacher_emails=teacher_emails))

    return dict(message="Success!", data=data)


@view_config(route_name="mb_homeroom", renderer="json")
def mb_homeroom(request):
    """
    Return teacher emails for every student who is in my homeroom
    """

    user = request.session.get('mb_user')
    if not user:
        return dict(message="No user in session?", data=[])
    if user.type != 'Advisors':
        return dict(message="Not a teacher", data=[])
    data = []
    with DBSession() as session:
        students = session.query(Students).filter_by(homeroom_advisor=user.id).all()
        for student in students:
            try:
                teachers = session.query(Teachers.email).\
                    select_from(Students).\
                        join(Enrollments, Enrollments.c.student_id == student.student_id).\
                        join(Courses, Courses.id == Enrollments.c.course_id).\
                        join(Assignments, Assignments.c.course_id == Courses.id).\
                        join(Teachers, Teachers.id == Assignments.c.teacher_id).\
                            all()
            except NoResultFound:
                continue

            teacher_emails = ",".join(set([t.email for t in teachers]))
            if teacher_emails:
                data.append(dict(student_email=teacher_emails, student_name=student.first_name + ' ' + student.last_name))
    return dict(message="Success", data=data)

@view_config(route_name="mb_courses", renderer='json', http_cache=0)
def mb_courses(request):
    user = request.session.get('mb_user')
    if not user:
        return dict(message="No user in session?")
    if not hasattr(user, 'classes'):
        return dict(message="User doesn't have classes?")
    data = []
    for klass in user.classes:
        grade_str = re.search('\((.*?)\)', klass.name)
        if grade_str:
            str = grade_str.group(1)
            grade_str = {0:None, 'Grade 10': 10, 'Grade 11': 11, 'Grade 12': 12}.get(str, int(re.sub('[^0-9]', '', str) or 0))
        else:
            grade_str = ""
        if grade_str is not None:
            data.append( dict(name=klass.abbrev_name, sortby=(grade_str, klass.uniq_id), shortname=klass.uniq_id, link='https://igbis.managebac.com/classes/{}'.format(klass.id)) )
    return dict(message="Success", data=sorted(data, key= lambda x: x['sortby'], reverse=True))

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

    params = request.params

    if not params:
        with DBSession() as session:
            statement = session.query(Students)
            students = statement.all()

        return dict(title="All Students", items=students)

    else:
        with DBSession() as session:
            statement = session.query(Students).filter_by(**params)
            students = statement.all()            

        return dict(title="Filtered Students", items=students)

@view_config(route_name='students_program_list', renderer='templates/students.pt')
def students_program_filter(request):
    m = request.matchdict
    program = m.get('program').lower()
    program_string = dict(pyp='IB PYP', dp="IB DP", myp="IB MYP")

    with DBSession() as session:
        statement = session.query(Students).filter_by(program=program_string.get(program))
        students = statement.all()

    return dict(title="All Students", items=students)


@view_config(route_name='students_ind', renderer='templates/student.pt')
def students_ind(request):
    return dict(title="Student View", item=None)
    m = request.matchdict
    student_id = m.get('id')
    if not student_id:
        return dict(items=[])

    with DBSession() as session:
        statement = session.query(Students).filter(Students.id == student_id)
        student = statement.one()

    return dict(title="Student View", item=student)

@view_config(route_name='user_data', renderer='json', http_cache=0)
def user_data(request):
    if not 'mb_user' in request.session:
        return dict(message="user_data: no user in sesssion")

    user = request.session.get('mb_user')
    return dict(message="success", data=user.first_name)

@view_config(route_name='get_user_settings', renderer='json', http_cache=0)
def get_user_settings(request):
    if not 'g_plus_unique_id' in request.session:
        return dict(message="get_user_settings: no user in sesssion")
    settings = None
    g_plus_unique_id = request.session.get('g_plus_unique_id')
    if g_plus_unique_id:
        with DBSession() as session:
            try:
                settings = session.query(UserSettings).filter_by(unique_id=g_plus_unique_id).one()
            except NoResultFound:
                pass
    else:
        return dict(message="g_plus_unique_id not in session", data=settings)

    data = {'icon_size':settings.icon_size}
    return dict(message="success", data=data)

@view_config(route_name='user_settings', renderer='json')
def user_settings(request):
    unique_id = request.session.get('g_plus_unique_id')
    if not unique_id:
        return dict(message="No unique_id in session")

    icon_size = request.json.get('icon_size')
    if icon_size:
        with DBSession() as session:
            try:
                setting = session.query(UserSettings).filter_by(unique_id=unique_id).one()
                if setting.icon_size != icon_size:
                    setting.icon_size = icon_size
                    return dict(message="Updated setting record to {}".format(setting.icon_size))
                return dict(message="Message received but no need to update")
            except NoResultFound:
                new_setting = UserSettings(unique_id=unique_id, icon_size=icon_size, new_tab=True)
                session.add(new_setting)
                return dict(message="Created new setting record in db")

    new_tab = request.json.get('new_tab')
    if new_tab:
        with DBSession() as session:
            try:
                setting = session.query(UserSettings).filter_by(unique_id=unique_id).one()
                if setting.new_tab != new_tab:
                    setting.new_tab = new_tab
                    return dict(message="Updated setting record to {}".format(setting.new_tab))
                return dict(message="Message received but no need to update")
            except NoResultFound:
                new_setting = UserSettings(unique_id=unique_id, new_tab=bool(int(new_tab)))
                session.add(new_setting)
                return dict(message="Created new setting record in db")

@view_config(route_name='reports_ind', renderer='templates/report_ind.pt')
def reports_ind(request):
    student_id = request.GET.get('student_id')
    

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

@view_config(context=ReportIncomplete)
def report_incomplete(request):
    response = Response()
    response.status_int = 500
    return response

@view_config(route_name='header-html', renderer='frontend:templates/header-html.pt')
def header_html(request):
    """
    Just return the headers
    """
    return dict()

@view_config(route_name='footer-html', renderer="frontend:templates/footer-html.pt")
def footer_html(request):
    """
    Just return the footer
    """
    student_id = request.GET.get('student_id')
    term_id = 27808
    with DBSession() as session:
        student = session.query(Students).filter_by(id=student_id).one()
        report  = session.query(PrimaryReport).\
            options(joinedload('course')).\
            filter_by(student_id=student.id, term_id=term_id).one()

    # FIXME: Including the below makes the footer always appear
    # I have no idea why, uncaching it???
    # template = 'frontend:templates/footer-html.pt'
    # result = render(template, 
    #     dict(
    #         student=student, 
    #         report=report
    #     ),
    #     request=request)

    # print('#\n' + result + '\n#')

    return dict(student=student, report=report)

@view_config(route_name='frontpage')
def frontpage(request):
    raise HTTPFound(request.route_url("splash"))

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
