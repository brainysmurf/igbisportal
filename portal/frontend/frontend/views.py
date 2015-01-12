# -*- coding: utf-8 -*-

"""
Defines the frontend behaviour
"""

from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload, joinedload_all

from portal.db import Database, DBSession
db = Database()

import json, re

import requests

from collections import namedtuple, OrderedDict

class ReportIncomplete(Exception):
    def __init__(self, msg):
        self.msg = msg

PREFIX = 'igbis2014'
url = 'https://{}.managebac.com/api/{{}}'.format(PREFIX)

api_token = 'a473e92458548d66c06fe83f69831fd5'

Students = db.table_string_to_class('student')
ReportComments = db.table_string_to_class('report_comments')
PrimaryReport = db.table_string_to_class('primary_report')
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

stndrdbttns = [
    button(name="ManageBac", url="https://igbis.managebac.com", icon="fire",
        context_menu={
        'items': [   
            menu_item(icon="user", display="HR Attendance", url="https://igbis.managebac.com/dashboard/attendance"),
            menu_item(icon="calendar-o", display="Calendar", url="https://igbis.managebac.com/home"),
            menu_item(icon="file-text-o", display="EE", url="https://igbis.managebac.com/dashboard/projects?type=ee")
        ],
        }),
    button(name="Gmail", url="https://gmail.com", icon="envelope", 
        context_menu={
        'items': [
            menu_item(icon="pencil", display="Compose", url="https://mail.google.com/mail/u/0/#inbox?compose=new")
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
            menu_item(icon="search", display="Catalog", url="http://blah"),
            menu_separator(),
            menu_item(icon="star", display='Elementary Britannica', url="http://school.eb.com.au/levels/elementary"),
            menu_item(icon="star", display='Middle Britannica', url="http://school.eb.com.au/levels/middle"),
            menu_item(icon="star", display='High Britannica', url="http://school.eb.com.au/levels/high")
        ],
        }),
    button(name="Calendar", url="https://www.google.com/calendar/", icon="calendar", context_menu=None),
]

@view_config(route_name='splash', renderer='templates/splash.pt')
def splash(request):
    role = request.GET.get('role', 'student')
    student_buttons = stndrdbttns[:]
    student_buttons.extend([
            button(name="BrainPop", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", context_menu=None),
            button(name="YouTube", url="http://youtube.com", icon="youtube", context_menu=None)
            ]
        )
    teacher_buttons = stndrdbttns[:]
    teacher_buttons.extend([
            button(name="Activities", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/", icon="rocket", 
            context_menu={
            'items': [
                menu_item(icon="rocket", display="Current Activities", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/current-activities"),
                menu_item(icon="plus-circle", display="Sign-up", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/sign-up"),
                menu_item(icon="user", display="Staff", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/staff"),
            ]
        }),
            button(name="Hapara Dashboard", url="https://teacherdashboard.appspot.com/igbis.edu.my", icon="dashboard", context_menu=None),
            button(name="InterSIS", url="https://igbis.intersis.com", icon="info-circle", 
            context_menu={
            'items': [
                menu_item(icon="user", display="Students", url="https://igbis.intersis.com/students?statuses=enrolled"),
                menu_item(icon="pencil", display='Messaging', url="https://igbis.intersis.com/messaging"),
                menu_item(icon="check-square-o", display='Attendance', url="https://igbis.intersis.com/attendance/students"),
            ],
        }),
            button(name="Secondary Principal", icon="trophy", url="", 
            context_menu={
            'items': [
                menu_item(icon="warning", display="Absences / Cover", url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/teacher-absences"),
                menu_item(icon="pencil", display='Sending Messages', url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/using-intersis-bulk-messaging")
            ],
        }),
            button(name="OCC", url="http://occ.ibo.org/ibis/occ/guest/home.cfm", icon="gear", context_menu=None),
            button(name="Book Geoff", url="https://geoffreyderry.youcanbook.me/", icon="thumb-tack", context_menu=None),
            button(name="IT Help Desk", url="http://rodmus.igbis.local/", icon="exclamation-circle", context_menu=None),
            button(name="BrainPop", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", 
            context_menu={
            'items': [
                menu_item(icon="external-link-square", display="Make sharable link", url="/brainpop"),
            ]
            }),
            button(name="YouTube", url="http://youtube.com", icon="youtube", context_menu=None)
            ]
        )
    buttons = OrderedDict()
    buttons['Teachers'] = teacher_buttons
    buttons['Students'] = student_buttons
    return dict(
        role=role, 
        title="[IGBIS] Splash",
        buttons = buttons,
    )

@view_config(route_name='hourofcode', renderer='templates/hourofcode.pt')
def hourofcode(request):
    role = request.GET.get('role', 'student')
    student_buttons = []
    teacher_buttons = []
    teacher_buttons.extend([
            button(name="Program a Game", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="gamepad", 
                context_menu={
                'items': [
                    menu_item(icon="dot-circle-o", display="Angry Birds", url="http://studio.code.org/s/course2/stage/3/puzzle/1"),
                    menu_item(icon="dot-circle-o", display='Plants vs Zombies', url="http://studio.code.org/s/course3/stage/2/puzzle/1"),
                    menu_separator(),
                    menu_item(icon="dot-circle-o", display='More! More!', url="http://studio.code.org/"),
                ]
                }
            ),
            button(name="Design a World", url="#", icon="codepen",
                context_menu={
                'items': [
                    menu_item(icon="dot-circle-o", display='Scratch Starter Projects', url="http://scratch.mit.edu/starter_projects/"),
                    menu_item(icon="dot-circle-o", display="Start with Stratch Online", url="http://scratch.mit.edu/projects/editor/?tip_bar=getStarted"),
                ]
                }
            ),
            button(name="Fiddle with Code", url="#", icon="code",
                context_menu={
                'items': [
                    menu_item(icon="dot-circle-o", display='Fiddle with a Website', url="http://jsfiddle.net/xpatm05k/"),
                    menu_item(icon="dot-circle-o", display='Fiddle with Tic Tac Toe', url="http://jsfiddle.net/rtoal/5wKfF/"),
                ]
                }
            ),
            button(name="Learn More", url="#", icon="question-circle",
                context_menu={
                'items': [
                    menu_item(icon="dot-circle-o", display='Introduction to Computer Science', url="http://www.brainpop.com/technology/computerscience/computerprogramming?user=igbisbrainpop&password=2014igbis"),
                    menu_item(icon="dot-circle-o", display="Learn to Code a Website", url="http://www.codecademy.com/en/tracks/web"),
                ]
                }
            ),
            ]
        )
    buttons = OrderedDict()
    buttons['Teachers'] = teacher_buttons
    buttons['Students'] = student_buttons
    return dict(
        role=role, 
        title="[IGBIS] Hour of Code",
        buttons = buttons,
    )


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

@view_config(context=ReportIncomplete)
def report_incomplete(request):
    response = Response()
    response.status_int = 500
    return response

@view_config(route_name='student_pyp_report', renderer='templates/student_pyp_report.pt')
def pyp_reports(request):
    m = request.matchdict
    student_id = m.get('id')
    internal_check = request.params.get('internal_check')
    term_id = 27807  # m.get('term_id')

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
        except NoResultFound:
            raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))
 
    subject_rank = {'language':0, 'mathematics':1, 'unit of inquiry 1':2, 'unit of inquiry 2':3, 'art':4, 'music':5, 'physical education':6, 'bahasa malaysia':7, 'chinese':8, 'host nation':9}
    report.sections = sorted(report.sections, key=lambda x: subject_rank.get(x.name.lower(), 1000))

    for section in report.sections:

        section.learning_outcomes = sorted(section.learning_outcomes, key=lambda x: x.which)

        # Standardize the headings
        en_dash = u'\u2013'
        for outcome in section.learning_outcomes:
            outcome.heading = outcome.heading.replace(en_dash, '-')
            match = re.match('(.*)-', outcome.heading)
            if match:
                outcome.heading = match.group(1).strip()

        # Evaluates and adds data to items
        old_heading = None
        for outcome in section.learning_outcomes:

            if outcome.heading != old_heading:
                # Mark that indicates we need to evaluate

                if subject_rank.get(section.name.lower()) in [0, 1, 7]:
                    # Determine the effort assigned by the teacher for this
                    effort = [s.selection for s in section.strands if s.label.startswith(outcome.heading)]
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

    return dict(
        title="Student Report",
        report= report,
        student=student
        )

@view_config(route_name="student_pyp_report_no", renderer='templates/student_pyp_report_no.pt')
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
