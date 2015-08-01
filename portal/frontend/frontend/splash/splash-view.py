from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.renderers import render

from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DBAPIError

from portal.db import Database, DBSession
db = Database()

from collections import defaultdict, namedtuple, OrderedDict
import json, re, uuid

import gns

from sqlalchemy.orm import joinedload

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
UserDefinedTabs = db.table_string_to_class('user_defined_tabs')
UserDefinedButtons = db.table_string_to_class('user_defined_buttons')

button = namedtuple('button', ['externalid', 'name', 'color', 'size', 'url', 'icon', 'id', 'context_menu'])

menu_item = namedtuple('menu_item', ['display', 'url', 'icon'])
menu_separator = lambda : menu_item(url=None, display='hr', icon=None)
menu_placeholder = lambda x: menu_item(url=x, display='placeholder', icon=None)

stndrdbttns = [
    button(name="ManageBac", externalid=-9, size="large", color="red", url="https://igbis.managebac.com", icon="fire", id="",
        context_menu={
        'items': [
            menu_item(icon="user", display="HR Attendance", url="https://igbis.managebac.com/dashboard/attendance"),
            menu_item(icon="calendar-o", display="Calendar", url="https://igbis.managebac.com/home"),
            menu_item(icon="file-text-o", display="EE", url="https://igbis.managebac.com/dashboard/projects?type=ee"),
            menu_placeholder('mb_classes')
        ],
        }),
    button(name="Gmail", externalid=-9, size="", color="blue", url="https://gmail.com", icon="envelope", id="", 
        context_menu={
        'items': [
            menu_item(icon="pencil", display="Compose", url="https://mail.google.com/mail/u/0/#inbox?compose=new"),
        ]
        }),
    button(name="Google Drive", externalid=-9, size="", color="purple", url="https://drive.google.com", icon="files-o", id="", 
        context_menu={
        'items': [
            menu_item(icon="folder", display="Whole School", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERMjMtbFUwcWhPUTA"),
            menu_item(icon="folder", display="Elementary", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERQXRSaVJRS0RrZFk"),
            menu_item(icon="folder", display="Secondary", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERZ0RDRkhzWk5vdWs"),
            menu_separator(),
            menu_item(icon="question-circle", display="What else?", url="#")
        ]
        }),
    button(name="Google Plus", externalid=-9, size="", color="green", url="https://plus.google.com/", icon="google-plus", id="", context_menu=None),
    button(name="Library", externalid=-9, size="", color="yellow", url="https://igbis.follettdestiny.com", icon="university", id="", 
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
    button(name="Calendar", externalid=-9, size="", color="red", url="https://www.google.com/calendar/", icon="calendar", id="", context_menu=None),
    button(name="YouTube", externalid=-9, size="", color="aqua", url="http://youtube.com", icon="youtube", id="", context_menu=None),

    button(name="Music Academy", externalid=-9, size="", color="cyan", url="https://sites.google.com/a/igbis.edu.my/igbis-instrumental-music-academy/home?pli=1", icon="music", id="", context_menu=None)
]

emergency_button = button(name="Emergency Contact", externalid=-9, size="", color="yellow", url="https://sites.google.com/a/igbis.edu.my/emergency-contact-information/", icon="phone-square", id="", context_menu=None)
# intl_day_button = button(name="International Day", color=None, icon="smile-o", url="https://drive.google.com/drive/folders/0By29gsjYgr0EdS1WWFVRS1pTY1k", id="", 
#         context_menu={
#         'items': [
#             menu_item(icon="folder", display="Google Drive folder", url="https://drive.google.com/drive/folders/0By29gsjYgr0EdS1WWFVRS1pTY1k"),
#             menu_separator(),
#             menu_item(icon="file-text", display="Cultural Activities and Sports", url="https://docs.google.com/document/d/1UjvgvSdel_gonrq6ONngcZquIh-upTVU64Tw6_FWVKQ/edit"),
#             menu_item(icon="file-text", display="Nationality Lists", url="https://docs.google.com/spreadsheets/d/1qcKr_IFlDaL-4LiF5BswU5xG4aFKkTx096PQbUiVXtg/edit#gid=196206741"),
#             menu_separator(),
#             menu_item(icon="file-movie-o", display="Download Students Dancing", url="https://doc-00-5c-docs.googleusercontent.com/docs/securesc/884cabjr1sdneekvn44p41a882r4naec/3n5qsegs0a0651mtt09hhcijticoe6av/1431424800000/02981500850996571698/02981500850996571698/0B2Jx5iFaTuHJM0tfV0JYV2Q4Qjg?h=08807967339938854529&e=download"),
#         ],
#     })
ela_button = button(name="ELA Department", externalid=-9, size="", color="orange", url="https://sites.google.com/a/igbis.edu.my/igb-ela/", icon="folder-open", id="", context_menu=None)
bookings_button = button(name="Bookings", externalid=-9, size="", color="peach", url="https://sites.google.com/a/igbis.edu.my/bookings/", icon="bookmark", id="", context_menu=None)
ibo_button = button(name="IBO", externalid=-9, size="", color="orange", url="http://www.ibo.org/", icon="globe", id="", 
        context_menu={
        'items': [
            menu_item(icon="globe", display="PD Events & Workshops", url="http://www.ibo.org/en/professional-development/find-events-and-workshops/"),
            menu_item(icon="globe", display="IB Answers", url="https://ibanswers.ibo.org/"),
            menu_item(icon="globe", display="IB Store", url="https://store.ibo.org/"),
            menu_item(icon="globe", display="IB Blogs", url="http://blogs.ibo.org/")
        ],
        }
    )
cashless_button = button(name="Cashless", externalid=-9, size="", color="green", url="http://cashless.igbis.edu.my/", icon="money", id="", context_menu=None)

@view_config(route_name='updateButtons', renderer='json')
def update_buttons(request):
    return request.json

@view_config(route_name='splash', renderer='{}:splash/splash-template.pt'.format('frontend'), http_cache=0)
def splash(request):
    if not 'mb_user' in request.session and not 'gl_user' in request.session:
        unique = uuid.uuid4()  # random
        request.session['unique_id'] = str(unique)
        user_name = None
    else:
        if request.session.get('mb_user'):
            user_name = request.session['mb_user'].first_name
        elif request.session.get('gl_user'):
            user_name = request.session['gl_user'].first_name
        else:
            user_name = ""
        unique = None
    logged_in_user = request.session.get('mb_user', None)
    if not logged_in_user:
        logged_in_user = request.session.get('gl_user', None)

    student_buttons = stndrdbttns[:]
    student_buttons.extend([
        button(name="BrainPop", externalid=-9, size="", color="beige", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", id="", context_menu=None),
    ])

    sec_teacher_buttons = stndrdbttns[:]
    elem_teacher_buttons = stndrdbttns[:]
    elem_teacher_buttons.extend([
        ibo_button,
        button(name="Teacher Dashboard", externalid=-9, size="large", color="purple", url="https://teacherdashboard.appspot.com/igbis.edu.my", icon="dashboard", id="", context_menu=None),
        button(name="InterSIS", externalid=-9, size="", color="blue", url="https://igbis.intersis.com", icon="info-circle", id="", 
        context_menu={
        'items': [
            menu_item(icon="user", display="Students", url="https://igbis.intersis.com/students?statuses=enrolled"),
            menu_item(icon="pencil", display='Messaging', url="https://igbis.intersis.com/messaging"),
            menu_item(icon="check-square-o", display='Attendance', url="https://igbis.intersis.com/attendance/students"),
        ]}),
        button(name="Reports Hub", externalid=-9, size="", color="orange", url="reports_hub", icon="gavel", id="", context_menu=None),
        button(name="IT Help Desk", externalid=-9, size="", color="red", url="http://rodmus.igbis.local/", icon="exclamation-circle", id="", context_menu=None),
        button(name="BrainPop", externalid=-9, size="", color="beige", url="http://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", id="", context_menu=None),
        bookings_button,
        ela_button,
        emergency_button,
        cashless_button
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
        homeroom_items.append(menu_item(icon="", display=display.format(grade), url="mailto:{}".format(hroom_emails)))

    homeroom_items.append(menu_placeholder("mb_homeroom"))

    sec_teacher_buttons.extend([
        ibo_button,

        button(name="Homeroom", externalid=-9, size="", color="beige", url="notsure", icon="cube", id="", 
        context_menu={
        'items': homeroom_items}),

        button(name="Communications", externalid=-9, size="", color="cyan", url="dunno", icon="comments", id="", 
        context_menu={
        'items': [
            menu_item(icon="venus-mars", display="Staff Information Sharing", url="https://sites.google.com/a/igbis.edu.my/staff/welcome"),
            menu_placeholder('mb_grade_teachers')
        ]}),

        button(name="Activities", externalid=-9, size="", color="pink", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/", icon="rocket", id="", 
        context_menu={
        'items': [
            menu_item(icon="rocket", display="Current Activities", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/current-activities"),
            menu_item(icon="plus-circle", display="Sign-up", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/sign-up"),
            menu_item(icon="user", display="Staff", url="https://sites.google.com/a/igbis.edu.my/igbis-activities/staff"),
        ]}),

        button(name="Teacher Dashboard", externalid=-9, size="large", color="purple", url="https://teacherdashboard.appspot.com/igbis.edu.my", icon="dashboard", id="", context_menu=None),
        button(name="InterSIS", externalid=-9, size="", color="blue", url="https://igbis.intersis.com", icon="info-circle", id="", 
        context_menu={
        'items': [
            menu_item(icon="user", display="Students", url="https://igbis.intersis.com/students?statuses=enrolled"),
            menu_item(icon="pencil", display='Messaging', url="https://igbis.intersis.com/messaging"),
            menu_item(icon="check-square-o", display='Attendance', url="https://igbis.intersis.com/attendance/students"),
        ]}),

        button(name="Secondary Principal", externalid=-9, size="", color="peach", icon="trophy", url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal", id="", 
        context_menu={
        'items': [
            menu_item(icon="warning", display="Absences / Cover", url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/teacher-absences"),
            menu_item(icon="pencil", display='Sending Messages', url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/using-intersis-bulk-messaging")
        ]}),

        button(name="OCC", externalid=-9, size="", color="beige", url="http://occ.ibo.org/ibis/occ/guest/home.cfm", icon="gear", id="", context_menu={
        'items':[
            menu_item(icon="gear", display="ATL on the OCC", url="https://xmltwo.ibo.org/publications/DP/Group0/d_0_dpatl_gui_1502_1/static/dpatl/"),
        ]}),
        button(name="IT Integration", externalid=-9, size="", color="yellow", url="https://sites.google.com/a/igbis.edu.my/plehhcet/", icon="arrows", id="", context_menu={
        'items': [
            menu_item(icon="thumb-tack", display="Book Geoff", url="https://geoffreyderry.youcanbook.me/"),
            menu_item(icon="apple", display="An Apple a Day", url="https://sites.google.com/a/igbis.edu.my/plehhcet/an-apple-a-day"),
        ]}),
        button(name="IT Help Desk", externalid=-9, size="", color="red", url="http://rodmus.igbis.local/", icon="exclamation-circle", id="", context_menu=None),

        bookings_button,
        ela_button,
        emergency_button,
        cashless_button
    ])

    buttons = OrderedDict()

    if logged_in_user:
        account_type = logged_in_user.type
        if account_type == 'Advisors':
            buttons['Secondary_Teachers'] = sec_teacher_buttons
            buttons['Elementary_Teachers'] = elem_teacher_buttons
            #buttons['Students'] = student_buttons  # for debugging
        elif account_type == 'Students':
            buttons['Students'] = student_buttons
        else:
            buttons['id'] = sec_teacher_buttons
            buttons['Elementary_Teachers'] = elem_teacher_buttons
            buttons['Students'] = student_buttons            
    else:
        buttons['Students'] = student_buttons

    g_plus_unique_id = request.session.get('g_plus_unique_id')
    settings = None
    if g_plus_unique_id:
        with DBSession() as session:
            try:
                settings = session.query(UserSettings).filter_by(unique_id=g_plus_unique_id).one()
                # tabs = session.query(UserDefinedTabs).\
                #     options(joinedload('buttons')).\
                #     filter_by(unique_id=g_plus_unique_id).all()
                # for tab in tabs:
                #     buttons[tab.name] = tab.buttons

            except NoResultFound:
                settings = None
                tabs = None

    return dict(
        client_id=gns.config.google.client_id,
        unique=unique,
        name=user_name,
        data_origin=gns.config.google.data_origin,
        title="IGBIS Splash Page",
        buttons = buttons,
        settings = settings
    )


