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

from portal.db import Database, DBSession
db = Database()

import json, re, uuid
from collections import defaultdict

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import requests

from collections import namedtuple, OrderedDict

import portal.settings as settings
import gns
settings.get('DIRECTORIES', 'home')
settings.get('GOOGLE', 'client_id')
settings.get('GOOGLE', 'data_origin')
settings.get('API', 'secret')

@view_config(route_name="frontpage")
def frontpage(request):
    return HTTPFound(location="splash")

class ReportIncomplete(Exception):
    def __init__(self, msg):
        self.msg = msg

Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')
Enrollments = db.table_string_to_class('enrollment')
Assignments = db.table_string_to_class('assignment')
ReportComments = db.table_string_to_class('report_comments')
PrimaryReport = db.table_string_to_class('primary_report')
Courses = db.table_string_to_class('course')
Absences = db.table_string_to_class('PrimaryStudentAbsences')
HRTeachers = db.table_string_to_class('secondary_homeroom_teachers')
GSignIn = db.table_string_to_class('google_sign_in')
UserSettings = db.table_string_to_class('user_settings')

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
    user_email = credentials.id_token.get('email')

    access_token = credentials.access_token

    if not user_email:
        return dict(message="Error: No user email detected?\n{}".format(str(credentials.id_token)))

    user = None
    with DBSession() as session:
        student = session.query(Students).filter_by(email=user_email).options(joinedload('classes')).first()
        if student:
            user = student
        if not user:
            teacher = session.query(Teachers).filter_by(email=user_email).options(joinedload('classes')).first()
            if teacher:
                user = teacher

        if not user:
            return dict(message="Error, could not find email {}".format(user_email))

        unique_id = credentials.id_token['sub']
        if user.g_plus_unique_id != unique_id:
            user.g_plus_unique_id = unique_id

    request.session['mb_user'] = user
    request.session['g_plus_unique_id'] = unique_id

    return dict(message="User found on ManageBac")

def credentials_flow(request, code):
    try:
        oauth_flow = \
            flow_from_clientsecrets(
                gns('{settings.home}/portal/frontend/client_secret.json'), 
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
            if result_json['issued_to'] != gns.settings.client_id:
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
            data.append(dict(student_email=teacher_emails, student_name=student.first_name + ' ' + student.last_name))
    return dict(message="Success", data=data)

@view_config(route_name='api-students', renderer='json')
def api_students(request):
    payload = request.params.get('secret')
    as_multidimentional_arrays = request.params.get('as_multidimentional_arrays')
    data = []
    if payload != gns.settings.secret:
        return dict(message="wrong secret", data=data)

    with DBSession() as session:
        data = session.query(Students).all()

    data.sort(key=lambda x: (x.first_name, x.last_name))

    columns = list(Students.__table__.columns.keys())

    if as_multidimentional_arrays:
        ret = [[getattr(data[row], columns[col]) for col in range(len(columns))] for row in range(len(data))]
        columns = [[columns[column] for column in range(len(columns))] for row in range(1)]
        return dict(message="Success, as array", columns=columns, data=ret)
    else:
        return dict(message="Success", columns=columns, data=[d.as_dict() for d in data])


@view_config(route_name="mb_courses", renderer='json')
def mb_courses(request):
    user = request.session.get('mb_user')
    if not user:
        return dict(message="No user in session?")
    if not hasattr(user, 'classes'):
        return dict(message="User doesn't have classes?")
    data = []
    for klass in user.classes:
        data.append( dict(name=klass.name, shortname=klass.uniq_id, link='https://igbis.managebac.com/classes/{}'.format(klass.id)) )
    return dict(message="Success", data=data)

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

button = namedtuple('button', ['name', 'url', 'icon', 'context_menu'])

menu_item = namedtuple('menu_item', ['display', 'url', 'icon'])
menu_separator = lambda : {'url':None}
menu_placeholder = lambda x: {'url': False, 'name':x}

stndrdbttns = [
    button(name="ManageBac", url="https://igbis.managebac.com", icon="fire",
        context_menu={
        'items': [
            menu_item(icon="user", display="HR Attendance", url="https://igbis.managebac.com/dashboard/attendance"),
            menu_item(icon="calendar-o", display="Calendar", url="https://igbis.managebac.com/home"),
            menu_item(icon="file-text-o", display="EE", url="https://igbis.managebac.com/dashboard/projects?type=ee"),
            menu_placeholder('mb_classes')
        ],
        }),
    button(name="Gmail", url="https://gmail.com", icon="envelope", 
        context_menu={
        'items': [
            menu_item(icon="pencil", display="Compose", url="https://mail.google.com/mail/u/0/#inbox?compose=new"),
        ]
        }),
    button(name="Google Drive", url="https://drive.google.com", icon="files-o", 
        context_menu={
        'items': [
            menu_item(icon="folder", display="Whole School", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERMjMtbFUwcWhPUTA"),
            menu_item(icon="folder", display="Elementary", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERQXRSaVJRS0RrZFk"),
            menu_item(icon="folder", display="Secondary", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERZ0RDRkhzWk5vdWs"),
            menu_separator(),
            menu_item(icon="question-circle", display="What else?", url="#")
        ]
        }),
    button(name="Library", url="https://igbis.follettdestiny.com", icon="university", 
        context_menu={
        'items': [
            menu_item(icon="search", display="Elementary Catalog", url="https://igbis.follettdestiny.com/cataloging/servlet/presentadvancedsearchredirectorform.do?l2m=Library%20Search&tm=TopLevelCatalog&l2m=Library+Search"),
            menu_item(icon="search", display="Secondary Catalog", url="https://igbis.follettdestiny.com/common/servlet/presenthomeform.do?l2m=Home&tm=Home&l2m=Home"),
            menu_separator(),
            menu_item(icon="star", display='Elementary Britannica', url="http://school.eb.com.au/levels/elementary"),
            menu_item(icon="star", display='Middle Britannica', url="http://school.eb.com.au/levels/middle"),
            menu_item(icon="star", display='High Britannica', url="http://school.eb.com.au/levels/high"),
            menu_placeholder('gd_starred')
        ],
        }),
    button(name="Calendar", url="https://www.google.com/calendar/", icon="calendar", context_menu=None),
]

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

@view_config(route_name='header-html', renderer='templates/header-html.pt')
def header_html(request):
    """
    Just return the headers
    """
    return dict()

@view_config(route_name='footer-html', renderer="templates/footer-html.pt")
def footer_html(request):
    """
    Just return the footer
    """
    student_id = request.GET.get('student_id')
    term_id = 27807
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

@view_config(route_name='student_pyp_report_with_opt')
@view_config(route_name='student_pyp_report')
def pyp_reports(request):
    m = request.matchdict
    student_id = m.get('id')
    pdf = m.get('pdf')
    if pdf and len(pdf) == 1:
        pdf = pdf[0]

    internal_check = request.params.get('internal_check')
    term_id = 27807  # m.get('term_id')

    with DBSession() as session:
        try:
            report = session.query(PrimaryReport).\
                options(joinedload('course')).\
                filter_by(term_id=term_id, student_id=student_id).one()
            student = session.query(Students).filter_by(id=student_id).one()
        except NoResultFound:
            raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

    title = "IGB International School (February 2015): Student Report for {} {}".format(student.first_name, student.last_name)

    # This bit is the only manual info that isn't on managebac
    uoi_table = {
        -1: {
            1: dict(title="Who We Are", central_idea="Everyday I can learn about who I am with and through others"),
            2: dict(title="Sharing The Planet", central_idea="We share the environment with a variety of creatures and it is important to respect their lives"),
            3: dict(title="No such unit", central_idea="Nope"),
        },
        0: {
            1: dict(title="Who We Are", central_idea="We are part of a community who work, live and learn together"),
            2: dict(title="How We Organise Ourselves", central_idea="People can create products or generate new ideas when they are given the opportunity to think and work independently and in groups"),
            3: dict(title="Where We Are in Place and Time", central_idea="Where and how we live determines what our home is like"),
        },
        1: {
            1: dict(title="How we organize ourselves", central_idea="Humans use maps to understand and organize their environment"),
            2: dict(title="Who we are", central_idea="Exploring different learning styles helps individuals understand each other better"),
            3: dict(title="How we express ourselves", central_idea="Celebrations are an opportunity to reflect and appreciate cultures and beliefs"),
        },
        2: {
            1: dict(title="Who we are", central_idea="All humans have rights and responsibilities which help them live together"),
            2: dict(title="Sharing The Planet", central_idea="Plants sustain life on earth and play a role in our lives"),
            3: dict(title="Where we are in Place and Time", central_idea="Individuals can influence us by their actions and contributions to society"),
        },
        3: {
            1: dict(title="Sharing the Planet", central_idea="Through our actions and lifestyles  we can improve how we care for the world"),
            2: dict(title="Who We Are", central_idea="Exercise and nutrition have an effect on how our body systems operate"),
            3: dict(title="How We Organise Ourselves", central_idea="Technology changes the way in which people work together"),
        },
        4: {
            1: dict(title="Who We Are", central_idea="People's beliefs influence their actions"),
            2: dict(title="How We Express Ourselves", central_idea="Media influences how we think and the choices we make"),
            3: dict(title="Where we Are in Place and Time", central_idea="Exploration leads to discovery and develops new understandings"),
        },
        5: {
            1: dict(title="Sharing The Planet", central_idea="The choices we make during moments of conflict affect our relationships"),
            2: dict(title="Where we are in Place and Time", central_idea="Change affects personal histories and the future"),
            3: dict(title="How we Organise Ourselves", central_idea="Understanding time helps us to plan and organize our lives"),
        },
    }

    chinese_teachers = {
        11131269:     # Anderina
            [10893375, 10837001, 11080391, 10866875, 10834622, 11080393, 10882226, 10882227, 10834621, 10866876],
        10792613:     # Xiaoping
            [10834635, 10882225, 10834617, 10834649, 10834618, 10836999, 10867797, 10893379, 10986169, 10837002, 10863230, 10867796, 10882159, 10882159, 10868400, 10834632, 10863220, 10863229, 10863228, 10973671],
        10792617:     # Mu Rong
            [10834645, 10866873, 10912651, 10834633, 10882155, 10834642, 10866172, 10834661],
        10792610:     # Yu Ri
            [10834656, 10834637, 10836998, 10856827, 10912650, 10834665, 10882152]
    }

    students_chinese_teachers = {}

    for teacher_id, student_ids in chinese_teachers.items():
        with DBSession() as session:
            teacher = session.query(Teachers).filter_by(id=teacher_id).one()
            for this_student in student_ids:
                students_chinese_teachers[this_student] = teacher

    if 'Grade' in report.course.name or 'Kindergarten' in report.course.name:
        which_folder = 'grades'
        template = 'frontend:templates/student_pyp_report.pt'

        with DBSession() as session:
            try:
                report = session.query(PrimaryReport).\
                    options(joinedload('course')).\
                    options(joinedload('sections')).\
                    options(joinedload('sections.learning_outcomes')).\
                    options(joinedload('sections.teachers')).\
                    options(joinedload('sections.strands')).\
                    options(joinedload('teacher')).\
                    filter_by(term_id=term_id, student_id=student_id).one()
                student = session.query(Students).filter_by(id=student_id).one()
                attendance = session.query(Absences).filter_by(term_id=term_id, student_id=student_id).one()
            except NoResultFound:
                raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

        subject_rank = {'language':0, 'mathematics':1, 'unit of inquiry 1':2, 'unit of inquiry 2':3, 'unit of inquiry 3':4, 'art':5, 'music':6, 'physical education':7, 'bahasa melayu':8, 'chinese':9, 'host nation':10, 'self-management':10000}
        report.sections = sorted([section for section in report.sections if subject_rank.get(section.name.lower()) < 10000], key=lambda x: subject_rank.get(x.name.lower(), 1000))

        # Only output sections that have any data in them
        # Comment out during development
        report.sections = [section for section in report.sections if section.comment]

        if 'Kindergarten' in report.course.grade:
            grade_norm = 0
        else:
            grade_norm = int(re.sub("[^0-9]", "", report.course.grade))

        uoi_units = [r for r in report.sections if 'unit of inquiry' in r.name.lower()]
        if len(uoi_units) == 3:
            pagination_list = [0, 1, 4, 7, 10]
        elif len(uoi_units) == 2:
            pagination_list = [0, 1, 3, 7, 10]
        elif len(uoi_units) == 1:
            pagination_list = [0, 1, 2, 7, 10]
        else:
            pagination_list = []

        for section in report.sections:
            section.rank = subject_rank.get(section.name.lower())

            # Substitute the correct Chinese teachers based on manual info above
            # Do first so all subsequent operations take place properly
            if section.rank == 9 and student.id in students_chinese_teachers:
                section.teachers = [students_chinese_teachers.get(student.id)]

            section.append_uoi_table = section.rank in [4]
            section.display_rotated = section.rank in [0, 1, 2, 5, 8, 9]

            if section.rank == 2:
                section.organization_header = "Units of Inquiry"
                section.name_after = ""
            elif section.rank in [3, 4]:
                section.organization_header = 'skip'
                section.name_after = ""
            else:
                section.organization_header = None
                section.name_after = ' (' + " & ".join([s.first_name + ' ' + s.last_name for s in section.teachers]) + ')'

            # Set the unit title if it needs to be
            if section.rank in [2, 3, 4]:
                which_uoi = int(re.sub("[^0-9]", "", section.name))
                section.name = uoi_table.get(grade_norm)[which_uoi]['title']

            # Determine pagination
            if section.rank in pagination_list:  #TODO What about more than two inquiry units?
                section.pagination = True
            else:
                section.pagination = False

            section.learning_outcomes = sorted(section.learning_outcomes, key=lambda x: x.which)

            # Standardize the headings
            if section.rank in [2, 3, 4]:
                section.name = section.name.title()
                section.name_after = uoi_table.get(grade_norm)[which_uoi]['central_idea']


            en_dash = u'\u2013'
            for outcome in section.learning_outcomes:

                if section.rank in [2, 3, 4]:
                    # Unit of inquiry
                    outcome.heading = ""

                elif section.rank not in [0, 1]:
                    outcome.heading = ""  # blank

                else:
                    # If it's a subject that we care to keep the data, standardize the format:
                    outcome.heading = outcome.heading.replace(en_dash, '-')
                    match = re.match('(.*)-', outcome.heading)
                    if match:
                        outcome.heading = match.group(1).strip()


            # Evaluates and adds data to items
            old_heading = None
            for outcome in section.learning_outcomes:

                if outcome.heading != old_heading:
                    # Mark that indicates we need to evaluate

                    if section.rank in [0, 1]:
                        # Determine the effort assigned by the teacher for this
                        effort = [s.selection for s in section.strands if s.label_titled.startswith(outcome.heading)]
                        effort = effort[0] if len(effort) == 1 else (effort[0] if len(set(effort))==1 else "<?>")
                    else:
                        effort = [s.selection for s in section.strands if s.selection]
                        effort = effort[0] if len(set(effort)) == 1 else str(effort)
                    outcome.effort = {'G': "Good", 'N': "Needs Improvement", 'O': "Outstanding"}.get(effort, None)

                    if not outcome.effort and internal_check:
                        # Raise a problem here
                        raise ReportIncomplete('something')

                old_heading = outcome.heading

                if not outcome.selection and internal_check:
                    raise ReportIncomplete('something')



    elif 'Early' in report.course.name:
        which_folder = 'early_years'
        template = 'frontend:templates/student_pyp_ey_report.pt'

        with DBSession() as session:
            try:
                report = session.query(PrimaryReport).\
                    options(joinedload('course')).\
                    options(joinedload('sections')).\
                    options(joinedload('sections.learning_outcomes')).\
                    options(joinedload('sections.teachers')).\
                    options(joinedload('teacher')).\
                    filter_by(term_id=term_id, student_id=student_id).one()
                student = session.query(Students).filter_by(id=student_id).one()
                attendance = session.query(Absences).filter_by(term_id=term_id, student_id=student_id).one()
            except NoResultFound:
                raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

        subject_rank = {'self-management':-1, 'language':0, 'mathematics':1, 'unit of inquiry 1':2, 'unit of inquiry 2':3, 'unit of inquiry 3':4, 'art':5, 'music':6, 'physical education':7, 'bahasa melayu':8, 'chinese':9, 'host nation':10}
        report.sections = sorted([section for section in report.sections if subject_rank.get(section.name.lower()) < 10000], key=lambda x: subject_rank.get(x.name.lower(), 1000))

        # Only output sections that have any data in them
        # Comment out during development
        report.sections = [section for section in report.sections if section.comment]

        grade_norm = -1

        uoi_units = [r for r in report.sections if 'unit of inquiry' in r.name.lower()]

        if len(uoi_units) == 3:
            pagination_list = [0, 4, 7, 10]
        else:
            pagination_list = [0, 3, 7, 10]

        for section in report.sections:

            section.rank = subject_rank.get(section.name.lower())

            # Substitute the correct Chinese teachers based on manual info above
            if section.rank == 9 and student.id in students_chinese_teachers:
                section.teachers = [students_chinese_teachers.get(student.id)]

            if section.rank == 2:
                section.organization_header = "Units of Inquiry"
                section.name_after = ""
            elif section.rank in [3, 4]:
                section.organization_header = 'skip'
                section.name_after = ""
            else:
                section.organization_header = None
                section.name_after = ' (' + " & ".join([s.first_name + ' ' + s.last_name for s in section.teachers]) + ')'

            if section.rank in [2, 3, 4]:
                which_uoi = int(re.sub("[^0-9]", "", section.name))
                section.name = uoi_table.get(grade_norm)[which_uoi]['title']
                section.name_after = ""

            # Determine pagination
            if section.rank in pagination_list:  #TODO What about more than two inquiry units?
                section.pagination = True
            else:
                section.pagination = False

            if section.rank in [2, 3, 4]:
                section.name = section.name.title() 
                section.name_after = uoi_table.get(grade_norm)[which_uoi]['central_idea']

            section.learning_outcomes = sorted(section.learning_outcomes, key=lambda x: x.which)


    options={
        'quiet': '',
        'header-html': 'http://igbisportal.vagrant:6543/header-html',
        'header-spacing': '5',

        'footer-html': 'http://igbisportal.vagrant:6543/footer-html?student_id={}'.format(student.id),

        'print-media-type': '',

        'margin-left': '3mm',
        'margin-right': '3mm',
        'margin-bottom': '10mm'
        }

    if pdf:

        import pdfkit
 
        result = render(template,
                    dict(
                        title=title,
                        report=report,
                        student=student,
                        attendance=attendance,
                        pdf=True
                        ),
                    request=request)
 
        path = '/home/vagrant/igbisportal/pdf-downloads/{}/{}-{}{}-{}.pdf'.format(which_folder, grade_norm, student.first_name.replace(' ', ''), student.last_name.replace(' ', ''), student.id)
        pdffile = pdfkit.from_string(result, path, options=options)   # render as HTML and return as a string
        
        if pdf.lower() == "download":
            content_type = "application/octet-stream"

            response = FileResponse(path, request=request, content_type=content_type)
            response.content_disposition = "attachment; filename='{}.pdf'".format(title)
            return response

        else:
            content_type = "application/pdf"

            response = FileResponse(path, request=request, content_type=content_type)
            return response

    else:
        result = render(template,
                    dict(
                        title=title,
                        report=report,
                        student=student,
                        attendance = attendance,
                        pdf=False
                        ),
                    request=request)
        response = Response(result)
        return response


@view_config(route_name="student_pyp_report_no", renderer='frontend:templates/student_pyp_report_no.pt')
def pyp_reports_no(request):
    return dict(title="No Such report")

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
