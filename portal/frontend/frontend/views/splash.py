from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.renderers import render

from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload, joinedload_all

from portal.db import Database, DBSession
db = Database()

from collections import defaultdict, namedtuple, OrderedDict
import json, re, uuid


import portal.settings as settings
import gns


""" 
FIXME: There has got to be a better way to do this
"""
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

settings.get('DIRECTORIES', 'home')
settings.get('FRONTEND', 'package_name')

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

@view_config(route_name='splash', renderer='{}:templates/splash.pt'.format('frontend'), http_cache=0)
def splash(request):
    if not 'mb_user' in request.session:
        unique = uuid.uuid4()  # random
        request.session['unique_id'] = str(unique)
        user_name = None
    else:
        user_name = request.session['mb_user'].first_name
        unique = None

    role = request.GET.get('role', 'student')
    student_buttons = stndrdbttns[:]
    student_buttons.extend([
        button(name="BrainPop", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", context_menu=None),
        button(name="YouTube", url="http://youtube.com", icon="youtube", context_menu=None)
    ])

    sec_teacher_buttons = stndrdbttns[:]
    elem_teacher_buttons = stndrdbttns[:]
    elem_teacher_buttons.extend([
        button(name="Reports Hub", url="reports_hub", icon="gavel", context_menu=None),
        ])

    with DBSession() as session:
        hroom_teachers = session.query(Teachers.email, Students.class_year).\
            join(HRTeachers, HRTeachers.teacher_id == Teachers.id).\
            join(Students, Students.id == HRTeachers.student_id).\
            all()

        homeroom_teachers = defaultdict(list)
        for item in hroom_teachers:
            if item.class_year and int(item.class_year) >= 6:
                grade = int(item.class_year) - 1
                if not item.email in homeroom_teachers[grade]:
                    homeroom_teachers[grade].append(item.email)

    homeroom_items = []
    for grade in sorted(homeroom_teachers):
        these_teachers = homeroom_teachers[grade]
        hroom_emails = ",".join(these_teachers)
        base_display = "Grade {{}} HR {}"
        display = base_display.format("Teachers" if len(these_teachers) > 1 else "Teacher")
        homeroom_items.append(menu_item(icon="envelope", display=display.format(grade), url="mailto:{}".format(hroom_emails)))

    homeroom_items.append(menu_placeholder("mb_homeroom"))

    sec_teacher_buttons.extend([
        button(name="Homeroom", url="notsure", icon="cube", 
        context_menu={
        'items': homeroom_items}),

        button(name="Communications", url="dunno", icon="comments",
        context_menu={
        'items': [
            menu_item(icon="venus-mars", display="Staff Information Sharing", url="https://sites.google.com/a/igbis.edu.my/staff/welcome"),
            menu_placeholder('mb_grade_teachers')
        ]}),

        button(name="Activities", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/", icon="rocket", 
        context_menu={
        'items': [
            menu_item(icon="rocket", display="Current Activities", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/current-activities"),
            menu_item(icon="plus-circle", display="Sign-up", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/sign-up"),
            menu_item(icon="user", display="Staff", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/staff"),
        ]}),

        button(name="Hapara Dashboard", url="https://teacherdashboard.appspot.com/igbis.edu.my", icon="dashboard", context_menu=None),
        button(name="InterSIS", url="https://igbis.intersis.com", icon="info-circle", 
        context_menu={
        'items': [
            menu_item(icon="user", display="Students", url="https://igbis.intersis.com/students?statuses=enrolled"),
            menu_item(icon="pencil", display='Messaging', url="https://igbis.intersis.com/messaging"),
            menu_item(icon="check-square-o", display='Attendance', url="https://igbis.intersis.com/attendance/students"),
        ]}),

        button(name="Secondary Principal", icon="trophy", url="", 
        context_menu={
        'items': [
            menu_item(icon="warning", display="Absences / Cover", url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/teacher-absences"),
            menu_item(icon="pencil", display='Sending Messages', url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/using-intersis-bulk-messaging")
        ]}),

        button(name="OCC", url="http://occ.ibo.org/ibis/occ/guest/home.cfm", icon="gear", context_menu={
        'items':[
            menu_item(icon="gear", display="ATL on the OCC", url="https://xmltwo.ibo.org/publications/DP/Group0/d_0_dpatl_gui_1502_1/static/dpatl/"),
        ]}),
        button(name="IT Integration", url="https://sites.google.com/a/igbis.edu.my/plehhcet/", icon="arrows", context_menu={
        'items': [
            menu_item(icon="thumb-tack", display="Book Geoff", url="https://geoffreyderry.youcanbook.me/"),
            menu_item(icon="apple", display="An Apple a Day", url="https://sites.google.com/a/igbis.edu.my/plehhcet/an-apple-a-day"),
        ]}),
        button(name="IT Help Desk", url="http://rodmus.igbis.local/", icon="exclamation-circle", context_menu=None),
        button(name="BrainPop", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", 
        context_menu={
        'items': [
            menu_item(icon="external-link-square", display="Make sharable link", url="/brainpop"),
        ]}),

        button(name="YouTube", url="http://youtube.com", icon="youtube", context_menu=None)
    ])

    buttons = OrderedDict()
    #FIXME: Why need no spaces?
    buttons['SecondaryTeachers'] = sec_teacher_buttons
    buttons['ElementaryTeachers'] = elem_teacher_buttons
    buttons['Students'] = student_buttons
    #buttons['Settings'] = settings_buttons

    g_plus_unique_id = request.session.get('g_plus_unique_id')
    settings = None
    if g_plus_unique_id:
        with DBSession() as session:
            try:
                settings = session.query(UserSettings).filter_by(unique_id=g_plus_unique_id).one()
            except NoResultFound:
                pass

    return dict(
        client_id=gns.settings.client_id,
        unique=unique,
        name=user_name,
        data_origin=gns.settings.data_origin,
        role=role,
        title="IGBIS Splash Page",
        buttons = buttons,
        settings = settings
    )


