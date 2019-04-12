from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.renderers import render

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DBAPIError

from portal.db import Database, DBSession
db = Database()

from collections import defaultdict, namedtuple, OrderedDict
import json
import re
import uuid

import gns

from sqlalchemy.orm import joinedload

button = namedtuple('button', ['externalid', 'name', 'color', 'size', 'url', 'icon', 'id', 'context_menu'])

menu_item = namedtuple('menu_item', ['display', 'url', 'icon'])


def menu_separator(): return menu_item(url=None, display='hr', icon=None)


def menu_placeholder(x): return menu_item(url=x, display='placeholder', icon=None)


stndrdbttns = [
    button(name="ManageBac", externalid=-9, size="large", color="red", url="https://igbis.managebac.com", icon="fire", id="", context_menu=None),
    button(name="School Email", externalid=-9, size="", color="blue", url="https://gmail.com", icon="envelope", id="",
           context_menu=None),
    button(name="Google Drive", externalid=-9, size="large", color="cyan", url="https://drive.google.com", icon="files-o", id="",
           context_menu=None),
    button(name="Google Plus", externalid=-9, size="", color="green", url="https://plus.google.com/", icon="google-plus", id="", context_menu=None),
    button(name="Library", externalid=-9, size="large", color="yellow", url="https://igbis.follettdestiny.com", icon="university", id="",
           context_menu=None),
    button(name="Music Academy", externalid=-9, size="", color="cyan", url="https://sites.google.com/a/igbis.edu.my/igbis-instrumental-music-academy/home?pli=1", icon="music", id="", context_menu=None)
]

emergency_procedures = button(name="Emergency Procedures", externalid=-9, size="", color="beige", url="", icon="warning", id="", context_menu={
    'items': [
        menu_item(icon="globe", display="HR Telephone Ext List", url="https://docs.google.com/spreadsheets/d/1Uxec8eAbExMY3Esn54j9TATDV7DcNGYIHJH9g8T42Gs/edit"),
        menu_separator(),
        menu_item(icon="globe", display="Evacuation procedures — ES", url="https://docs.google.com/document/d/1rqCtEFrDTzSwkZLjzDvVpeD2_nZx67_fjl8vL-Fcwfs/edit"),
        menu_item(icon="globe", display="Lockdown procedures — ES", url="https://docs.google.com/document/d/1jI1Yh7WboPJHxGeNjTeephEPSKlYGVzs-Gdg_6WTyy0/edit"),
        menu_item(icon="globe", display="Evacuation procedures — SS", url="https://docs.google.com/document/d/1PQ5z2awRnUo5cE4ysv_mdki-DG9WuUoAQzDam_3JY_k/edit"),
        menu_item(icon="globe", display="Lockdown procedures — SS", url="https://docs.google.com/document/d/1eDSpZEEp7WpQA_YzwolHJq_uHr9USSTLfiV-4asG7is/edit"),
        menu_item(icon="globe", display="Lockdown attendance form", url="https://docs.google.com/a/igbis.edu.my/forms/d/e/1FAIpQLSfUA0oJPUnf3OCnjjzos8ybHIcJut3ZlkvDfFmC3NuRcWfk-A/viewform?c=0&w=1"),
        menu_item(icon="globe", display="Emergency protocols Manual", url="https://docs.google.com/document/d/1-UTe_G3m-OaI7xag1v41LWKgMUcBD8HdsuWt06m6Tb8/edit?ts=5a818d32"),
        menu_item(icon="globe", display="Incident Report", url="https://docs.google.com/document/d/1WYqUn--ZIJ-Vq_dBYyjfzUawdJJM5T0ApaIL75irhY8/edit"),
    ]
})

secondary_camps_button = button(name="Secondary Camps", externalid=-9, size="large", color="aqua", url="https://sites.google.com/igbis.edu.my/camps/home", icon="gittip", id="", context_menu=None)
box_of_books_button = button(name="Box of Books", externalid=-9, size="", color="aqua", url="https://igbis-school.boxofbooks.io/auth/page/signin", icon="dropbox", id="", context_menu=None)
import_my_calendar_button = button(name="Import My Calendar", externalid=-9, size="", color="green", url="https://docs.google.com/document/d/10vtZDIKfgRPsOjXSg21XKRAALD3Qs8o7Yy3VKogI8DY/edit#heading=h.q6jcd88fou46", icon="calendar", id="", context_menu=None)
personal_project = button(name="Personal Project", externalid=-9, size="", color="yellow", url="https://sites.google.com/igbis.edu.my/personalproject1718/home?authuser=0", icon="calendar", id="", context_menu=None)

daily_notices_button = button(name="Communications", externalid=-9, size="large", color="aqua", url="https://sites.google.com/a/igbis.edu.my/communications/", icon="comments", id="", context_menu={
    'items': [
        menu_item(icon="plus-circle", display="Add a Daily Notice", url="https://docs.google.com/a/igbis.edu.my/forms/d/1ni0lu4mzVFzHW8PxWyap8iUEYFjOjEi_z_ZjEDJaS-s/viewform"),
        menu_separator(),
        menu_item(icon="calendar-check-o", display="Today's Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/"),
        menu_item(icon="search", display="Search Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/notices-database")
    ]})

emergency_button = button(name="Emergency Contact", externalid=-9, size="", color="yellow", url="https://sites.google.com/a/igbis.edu.my/emergency-contact-information/", icon="phone-square", id="", context_menu=None)

ela_button = button(name="ELA Department", externalid=-9, size="", color="orange", url="https://sites.google.com/a/igbis.edu.my/igb-ela/", icon="folder-open", id="", context_menu=None)
bookings_button = button(name="Events &amp;&nbsp; Bookings Spaces", externalid=-9, size="", color="peach", url="javascript:void(0)", icon="bookmark", id="", context_menu={
    'items': [
        menu_item(icon="globe", display="Events & Field Trips", url="https://sites.google.com/a/igbis.edu.my/igbis-whole-school-procedures/events-at-igbis"),
        menu_item(icon="globe", display="Bookable Spaces", url="https://sites.google.com/a/igbis.edu.my/bookings/")
    ]
})
ibo_button = button(name="IBO", externalid=-9, size="", color="purple", url="https://www.ibo.org/", icon="globe", id="",
                    context_menu={
                        'items': [
                            menu_item(icon="globe", display="PD Events & Workshops", url="https://www.ibo.org/en/professional-development/find-events-and-workshops/"),
                            menu_item(icon="globe", display="IB Answers", url="https://ibanswers.ibo.org/"),
                            menu_item(icon="globe", display="IB Store", url="https://store.ibo.org/"),
                            menu_item(icon="globe", display="IB Blogs", url="https://blogs.ibo.org/")
                        ],
                    }
                    )

managebac_info_button = button(name="ManageBac Info", externalid=-9, size="", color="peach", url="https://sites.google.com/igbis.edu.my/attendancereporter/home", icon="info-circle", id="", context_menu=None)
ib_app_button = button(name="IGBIS Enrollment and Nationality", externalid=-9, size="", url="https://script.google.com/a/macros/igbis.edu.my/s/AKfycbyA_lbYY75Jc9PRwU4T0mdkdp7xdCyPcPsWXjYix33amJcVRnIiTMKxPZnperCDPc9e/exec", color="orange", icon="list-alt", id="", context_menu=None)
cashless_button = button(name="Cashless", externalid=-9, size="", color="green", url="https://cashless.igbis.edu.my/", icon="money", id="", context_menu={
    'items': [
        menu_item(icon="globe", display="Main / Top up", url="https://cashless.igbis.edu.my/"),
        menu_item(icon="globe", display="IGBIS Cashless Manual", url="https://docs.google.com/document/d/1oJ8eKaQfCfIUyezaElMJ5c_udlsUky1IP_TcmsLco2E"),
    ]
})
counselor_button_students = button(name="Counselor", externalid=-9, size="", color="green", url=" https://sites.google.com/a/igbis.edu.my/counsellingigbis/", icon="heart", id="", context_menu={
    'items': [
        menu_item(icon="globe", display="Request an Appointment", url="https://docs.google.com/a/igbis.edu.my/forms/d/1wV6-UkFN1wB-wQvM_rtUZBGjGTXXipZ8WYHpNqeAI0c/viewform?usp=send_form"),
        menu_separator(),
        menu_item(icon="globe", display="Information about Depression", url="https://sofeajohan020.wixsite.com/theadversary")
    ]
})
counselor_button_not_students = button(name="Student Services & Counseling", externalid=-9, size="large", color="green", url="https://sites.google.com/igbis.edu.my/sst2017/home", icon="heart", id="", context_menu=None)  # , context_menu={
#     'items': [
#         menu_item(icon="globe", display="Student Services Site", url="https://sites.google.com/a/igbis.edu.my/sst"),
#         menu_item(icon="globe", display="Counselling Site", url="https://sites.google.com/a/igbis.edu.my/counsellingigbis/"),
#         menu_separator(),
#         menu_item(icon="globe", display="Behaviour Report Form", url="https://docs.google.com/a/igbis.edu.my/forms/d/1aTxoKnpGjuY9DcNJ7UlTJ6egsjG8-FMYTLpjvM1jdbY/viewform?c=0&w=1"),
#         menu_separator(),
#         menu_item(icon="globe", display="Make Appointment with Mr Chris (EY-8)", url="https://www.google.com/calendar/selfsched?sstoken=UUozUVhiTGtmemhQfGRlZmF1bHR8OTFlZTUyMTEwNzRkMDUyYjIzMGUwOTNjMDAwYmNmN2U"),
#         menu_item(icon="globe", display="Make Appointment with Mrs Davidson (9-12)", url="https://www.google.com/calendar/selfsched?sstoken=UUt3TjltOHZ1a0NhfGRlZmF1bHR8ODVjNGRlNjE3Nzk3NjhmNWVkMzA2MjgxODA2M2VmNDI"),
#         menu_item(icon="globe", display="Counselling Appointments Reference", url="https://docs.google.com/document/d/1nB5BYvTw1hUIgoLyZbXGJhXqNuqIV3WhUCSIigtKOaY/edit"),
#         menu_separator(),
#         menu_item(icon="globe", display="Wednesday Homework Support Sign-up", url="https://docs.google.com/a/igbis.edu.my/forms/d/1l9vqLOyKLTNlTZBWwEKU9VJT1aAm3ff0iye1QwCcZY8/viewform"),
#         menu_item(icon="globe", display="Wednesday Homework Support Reference List", url="https://docs.google.com/spreadsheets/d/1uqx-9-b9nsAWLME4qQcZm2g7tLTHqxOW3zVtEpdEvtw/edit#gid=1946619930")
#     ]
#     })
counselor_button_parents = button(name="Counseling", externalid=-9, size="", color="green", url="https://sites.google.com/a/igbis.edu.my/counsellingigbis/", icon="heart", id="", context_menu=None)


parent_buttons = [
    button(name="ManageBac", externalid=-9, size="", color="red", url="https://igbis.managebac.com", icon="fire", id="", context_menu=None),
    button(name="School Email", externalid=-9, size="", color="green", url="https://gmail.com", icon="envelope", id="",
           context_menu=None),
    button(name="Google Drive", externalid=-9, size="", color="aqua", url="https://drive.google.com", icon="files-o", id="",
           context_menu=None),
    button(name="Library", externalid=-9, size="", color="yellow", url="https://igbis.follettdestiny.com", icon="university", id="",
           context_menu=None),
    button(name="Music Academy", externalid=-9, size="", color="cyan", url="https://sites.google.com/a/igbis.edu.my/igbis-instrumental-music-academy/home?pli=1", icon="music", id="", context_menu=None),
    button(name="Classes", externalid=-9, size="", color="orange", url="", icon="star", id="", context_menu={
        'items': [
                #menu_item(icon="globe", display="Early Years K", url="https://sites.google.com/a/igbis.edu.my/eyk/"),
                menu_item(icon="globe", display="Fireflies", url="https://blog.seesaw.me/firefliesigbis"),
                menu_item(icon="globe", display="Early Years", url="https://blog.seesaw.me/earlyyearsigbis"),
                menu_item(icon="globe", display="Kindergarten", url="https://blog.seesaw.me/kindergartenigbis"),
                menu_item(icon="globe", display="Grade 1", url="https://blog.seesaw.me/grade1igbis"),
                menu_item(icon="globe", display="Grade 2", url="https://blog.seesaw.me/grade2igbis"),
                menu_item(icon="globe", display="Grade 3", url="https://sites.google.com/igbis.edu.my/3b3h/home"),
                menu_item(icon="globe", display="Grade 4", url="https://blog.seesaw.me/grade4igbis"),
                menu_item(icon="globe", display="Grade 5", url="https://sites.google.com/igbis.edu.my/igbisg5-2018-19/home")
        ]
    }),
    button(name="Activities & Athletics", externalid=-9, size="", color="pink", url="https://sites.google.com/igbis.edu.my/athleticsactivities", icon="rocket", id="", context_menu=None),
    button(name="PVO", externalid=-9, size="", color="grey", url="https://sites.google.com/igbis.edu.my/pvo", icon="child", id="", context_menu={
        'items': [
            menu_item(icon="book", display="Parents Volunteer Organization main site", url="https://sites.google.com/igbis.edu.my/pvo"),
            menu_separator(),
            menu_item(icon="book", display="Community Information (Class Reps Only)", url="https://sites.google.com/igbis.edu.my/communicationsforparents/home"),
        ]}),
    button(name="Calendar", externalid=-9, size="", color="peach", url="https://igbis.edu.my/news-events/upcoming-events/", icon="calendar", id="",
           context_menu={
               'items': [
                menu_item(icon="book", display="Upcoming Events", url="https://igbis.edu.my/news-events/upcoming-events/"),
                menu_item(icon="book", display="Rotating Timetable", url="https://docs.google.com/spreadsheets/d/1xzM6vgBV4_Bv0ZCD2IeNYfk95R_-wwl7FOlciMisF5Y"),
                menu_item(icon="book", display="Import My Timetable", url="https://docs.google.com/document/d/10vtZDIKfgRPsOjXSg21XKRAALD3Qs8o7Yy3VKogI8DY/edit#heading=h.q6jcd88fou46")
               ]
           }),
    button(name="Help", externalid=-9, size="", color="pink", url="https://sites.google.com/igbis.edu.my/parentpdpage/home", icon="calendar", id="", context_menu=None),
    cashless_button,
    button(name="Parent University", externalid=-9, size="", color="aqua", url="", icon="graduation-cap", id="https://drive.google.com/drive/folders/0B6wQr4eqP1FfNG1IVENHVkV5T2c", context_menu={
        'items': [
            menu_item(icon="folder", display="Session 1", url="https://drive.google.com/drive/folders/0B6wQr4eqP1FfX2JqbkNnYVhuWVU"),
            menu_item(icon="folder", display="Session 2", url="https://drive.google.com/drive/folders/0B6wQr4eqP1FfdTBYYlRqZ2tJUkE"),
        ]
    }),
    button(name="IGBIS Haze Policy", externalid=-9, size="", color="green", url="https://docs.google.com/document/d/15jFcNV7IkGMqWp6P90CVF3jp-QNWcBLTOzP39eT7v4M/edit?ts=5a1f4a22", icon="soundcloud", id="", context_menu=None),
    button(name="Food Services", externalid=-9, size="", color="green", url="https://igbis.edu.my/community/food-services/", icon="spoon", id="", context_menu=None),
    button(name="DP Programme", externalid=-9, size="", color="", url="https://sites.google.com/igbis.edu.my/diplomaprogramme", icon="graduation-cap", id="", context_menu=None),
    button(name="Houses", externalid=-9, size="", color="orange", url="https://sites.google.com/igbis.edu.my/igbhouses/home", icon="home", id="", context_menu=None),
    secondary_camps_button,
    personal_project
]

handbook_button = button(name="Staff Handbook", externalid=-9, size="", color="red", url="https://drive.google.com/drive/folders/0By9YOJwliLtBQm43NHBqd0FKM28", icon="book", id="",
                         context_menu={
                             'items': [
                                 menu_item(icon="book", display="Overview", url="https://docs.google.com/document/d/1dzZfzYOrWeOrpiw2ZFQAUL3th3VNFO1HbS7PvF3ECvQ/"),
                                 menu_item(icon="book", display="Organisation", url="https://docs.google.com/document/d/1ak57-lHwVvVLGKQdKKBVhWwFtbN_lE19ErRb9CkLTEE/"),
                                 menu_item(icon="book", display="Health and Safety", url="https://docs.google.com/document/d/1CttoZfwCbNW8fEQoAjzYj1cTQAxb3dRSxQ_KP2Py56I/"),
                                 menu_item(icon="book", display="Responsibilities of Teachers", url="https://docs.google.com/document/d/1W3e6q76oB8CVoToY5DUqyppK3iOzE2xGyllVQmofKLU/"),
                                 menu_item(icon="book", display="Elementary and Secondary Procedures", url="https://docs.google.com/a/igbis.edu.my/document/d/16q0RkQb2yNj4KCnSRrb9wxNZtP7MYV7ScrZjWuqMSyc/"),
                                 menu_item(icon="book", display="Budget and Supply Procedures", url="https://docs.google.com/a/igbis.edu.my/document/d/15WKjGWttfUkgu8CGahS0QeAzs07dBpwOyMZuyq2c_8k/"),
                                 menu_item(icon="book", display="HR Policies and Procedures", url="https://docs.google.com/a/igbis.edu.my/document/d/1UDyWngXoTLRJLOp0zyXAH788vaEePJzBmkNjcHlnOpA/"),
                                 menu_item(icon="book", display="School Policies", url="https://docs.google.com/document/d/1KvWIKahoSgcvfSNbnBuMqqFb6uB96PW5Fx7BqfptXvo"),
                                 menu_item(icon="book", display="Business Team Policies & Procedures", url="https://docs.google.com/document/d/1AYeVY1UZ970zwuh9fEwu5f7hcXdej--TyMw4PemDnHM"),
                             ]
                         })

administration_buttons = [

    button(name="Google Drive", externalid=-9, size="large", color="cyan", url="https://drive.google.com", icon="files-o", id="",
           context_menu={
               'items': [
                menu_item(icon="folder", display="Whole School", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERMjMtbFUwcWhPUTA"),
                menu_item(icon="folder", display="Elementary", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERMzM2M0ZJbzJzT1U"),
                menu_item(icon="folder", display="Secondary", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERZ0RDRkhzWk5vdWs"),
                menu_separator(),
                menu_item(icon="folder", display="Policies & Procedures", url="https://drive.google.com/open?id=0B_el10BYGhjLfkd1NmZHa3ZCdUxaRlVTSDVEdjVraHh2S053WEFjZFRSeHdzNldpRmNIZFk"),
                menu_item(icon="folder", display="CIS/NEASC Accreditation", url="https://drive.google.com/drive/folders/0By9YOJwliLtBM0FxRHFEVWVEcVk"),
                menu_item(icon="folder", display="Insurance Forms", url="https://drive.google.com/drive/folders/1Nz7s1LLuuZ8VIrjK7mQlojnsxeK0OHrn"),
                menu_separator(),
                menu_item(icon="folder", display="Instrumental Music Academy", url="https://docs.google.com/spreadsheets/d/1pqdrV3uaHChzrcUEC-6UMwZOrrdyQH_PaVyr4OuXu90/edit#gid=0"),
                menu_item(icon="folder", display="SS Camps", url="https://docs.google.com/spreadsheets/d/1l4rF_xnyy3hjKOGftBaOfnACq-PIz2hgT2uIR_Jyd2g/edit#gid=798482198"),
               ]
           }),
    button(name="Community Information", externalid=-9, size="large", color="aqua", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/home", icon="comments-o", id="", context_menu={
        'items': [
            menu_item(icon="plus-circle", display="Student Directory", url="https://script.google.com/a/macros/igbis.edu.my/s/AKfycbyA_lbYY75Jc9PRwU4T0mdkdp7xdCyPcPsWXjYix33amJcVRnIiTMKxPZnperCDPc9e/exec#Directory/"),
            menu_item(icon="plus-circle", display="Medical Information", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/medical-info"),
            menu_item(icon="plus-circle", display="Bulk Email App", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/bulk-email-app"),
            menu_separator(),
            menu_item(icon="plus-circle", display="Add a Daily Notice", url="https://docs.google.com/a/igbis.edu.my/forms/d/1ni0lu4mzVFzHW8PxWyap8iUEYFjOjEi_z_ZjEDJaS-s/viewform"),
            menu_separator(),
            menu_item(icon="calendar-check-o", display="Today's Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/"),
            menu_item(icon="search", display="Search Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/notices-database")
        ]}),
    button(name="School Email", externalid=-9, size="", color="blue", url="https://gmail.com", icon="envelope", id="",
           context_menu=None),
    bookings_button,
    button(name="Calendar", externalid=-9, size="", color="peach", url="https://sites.google.com/a/igbis.edu.my/igbis-calendar/", icon="calendar", id="", context_menu=None),
    button(name="Help Desk: IT&nbsp;&amp;&nbsp;Facilities", externalid=-9, size="", color="red", url="http://rodmus.igbis.local/", icon="exclamation-circle", id="", context_menu=None),
    handbook_button,
    cashless_button,
    button(name="Admissions Information", externalid=-9, size="", color="aqua", url="https://sites.google.com/igbis.edu.my/infoforadmissions/home", icon="comment-o", id="", context_menu=None),
    emergency_procedures,
    ib_app_button
]


@view_config(route_name='updateButtons', renderer='json')
def update_buttons(request):
    gplus = request.session.get('g_plus_unique_id')
    if not gplus:
        return HTTPForbidden()
    with DBSession() as session:
        try:
            this = session.query(db.table.UserSplashJson).filter_by(id=request.session.get('g_plus_unique_id')).one()
            this.json = json.dumps(request.json)
        except NoResultFound:
            new = db.table.UserSplashJson(id=gplus, json=request.body)
            session.add(new)
            return request.json
    return dict(message="Success")


@view_config(route_name='getButtons', renderer='json')
def get_buttons(request):
    gplus = request.session.get('g_plus_unique_id')
    if not gplus:
        return "[]"  # fake array
    with DBSession() as session:
        try:
            this = session.query(db.table.UserSplashJson).filter_by(id=request.session.get('g_plus_unique_id')).one()
        except NoResultFound:
            return "[]"  # fake array
    return this.json


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
        button(name="Activities & Athletics", externalid=-9, size="large", color="pink", url="https://sites.google.com/igbis.edu.my/athleticsactivities", icon="rocket", id="", context_menu=None),
        button(name="BrainPop", externalid=-9, size="", color="beige", url="https://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", id="", context_menu=None),
        button(name="Photo Sharing", externalid=-9, size="", color="blue", url="https://sites.google.com/a/igbis.edu.my/elem-photo-sharing/", icon="picture-o", id="", context_menu=None),
        counselor_button_students,
        button(name="Houses", externalid=-9, size="", color="orange", url="https://sites.google.com/igbis.edu.my/igbhouses/home", icon="home", id="", context_menu=None),
        button(name="DP Programme", externalid=-9, size="", color="", url="https://sites.google.com/igbis.edu.my/diplomaprogramme", icon="graduation-cap", id="", context_menu=None),
        button(name="Student-led Event Proposal", externalid=-9, size="", id="", color="cyan", url="https://docs.google.com/document/d/1pmf8gUoFNAdCi6Uu_x5G0AZa1Ny6wP7z8muMXvLQ3io/copy", icon="calendar", context_menu=None),
        button(name="SPACPOL", externalid=-9, size="", id="", color="blue", url="https://goo.gl/forms/MuwkFFGjqHZ4TDvR2", icon="list-ul", context_menu=None),
        button(name="EOSMun19", externalid=-9, size="", id="", color="yellow", url="https://eosmun19.wixsite.com/2019-eosmun", icon="renren", context_menu=None),
        button(name="Abstract Reality by Marvin", externalid=-9, size="", id="", color="grey", url="https://www.kongregate.com/games/marvinch/abstract-reality", icon="gamepad", context_menu=None),
        personal_project
    ])

    with DBSession() as session:
        hroom_teachers = session.query(db.table.Teacher.email, db.table.Student.class_year).\
            select_from(db.table.Student).\
            join(db.table.Teacher, db.table.Teacher.id == db.table.Student.homeroom_advisor).\
            all()

        homeroom_teachers = defaultdict(list)
        for item in hroom_teachers:
            if item.class_year and int(item.class_year) >= 6:
                grade = int(item.class_year) - 1
                if not item.email in homeroom_teachers[grade]:
                    homeroom_teachers[grade].append(item.email)

    homeroom_items = [
        menu_item(icon="", display="Welfare Program", url="https://docs.google.com/document/d/1WqiKyyaEQs-FXILfmyFwERiK1KgUfaYpAVWk5MyAu4s/edit"),
    ]
    for grade in sorted(homeroom_teachers):
        these_teachers = homeroom_teachers[grade]
        hroom_emails = ",".join(these_teachers)
        base_display = "Email Grade {{}} HR {}"
        display = base_display.format("Teachers" if len(these_teachers) > 1 else "Teacher")
        homeroom_items.append(menu_item(icon="", display=display.format(grade), url="mailto:{}".format(hroom_emails)))

    homeroom_items.append(menu_placeholder("mb_homeroom"))

    sec_teacher_buttons = [
        button(name="ManageBac", externalid=-9, size="large", color="red", url="https://igbis.managebac.com", icon="fire", id="",
               context_menu={
                   'items': [
                    menu_item(icon="user", display="HR Attendance", url="https://igbis.managebac.com/dashboard/attendance"),
                    menu_separator(),
                    menu_item(icon="calendar-o", display="Assessment Data", url="https://sites.google.com/igbis.edu.my/assessment")
                   ],
               }),
        button(name="School Email", externalid=-9, size="", color="blue", url="https://gmail.com", icon="envelope", id="",
               context_menu={
                   'items': [
                    menu_item(icon="pencil", display="Compose", url="https://mail.google.com/mail/u/0/#inbox?compose=new"),
                   ]
               }),
        button(name="Google Drive", externalid=-9, size="large", color="cyan", url="https://drive.google.com", icon="files-o", id="",
               context_menu={
                   'items': [
                    menu_item(icon="folder", display="Whole School", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERMjMtbFUwcWhPUTA"),
                    menu_item(icon="folder", display="Elementary", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERMzM2M0ZJbzJzT1U"),
                    menu_item(icon="folder", display="Secondary", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERZ0RDRkhzWk5vdWs"),
                    menu_separator(),
                    menu_item(icon="folder", display="Policies & Procedures", url="https://drive.google.com/open?id=0B_el10BYGhjLfkd1NmZHa3ZCdUxaRlVTSDVEdjVraHh2S053WEFjZFRSeHdzNldpRmNIZFk"),
                    menu_item(icon="folder", display="CIS/NEASC Accreditation", url="https://drive.google.com/drive/folders/0By9YOJwliLtBM0FxRHFEVWVEcVk"),
                    menu_item(icon="folder", display="Insurance Forms", url="https://drive.google.com/drive/folders/1Nz7s1LLuuZ8VIrjK7mQlojnsxeK0OHrn"),
                    menu_separator(),
                    menu_item(icon="folder", display="MYP Resources", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERclEzb3Zpa3dMcjg"),
                    menu_item(icon="folder", display="MYP Guides", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERNWMtOU02U0ZkdHc"),
                    menu_item(icon="folder", display="MYP Subject Overviews", url="https://docs.google.com/spreadsheets/d/19DVirR29E8KTmsSri73udVPBltES6j5xnpTUj2E-ZUc/"),
                    menu_separator(),
                    menu_item(icon="folder", display="Teacher Timetables", url="https://docs.google.com/spreadsheets/d/1Hp1lJkDCEVzRl_BpozWq_wpBW-1DnUPUm_qy4h6qGks/edit"),
                    #menu_item(icon="folder", display="Class Timetables", url="https://docs.google.com/a/igbis.edu.my/spreadsheets/d/1m77dkYjRwxo4JUClMbHTvYRh4BEeRZKR-DBgIABKbCY"),
                    menu_item(icon="folder", display="SS Duty Schedule", url="https://docs.google.com/spreadsheets/d/1t6wvDQpiweS9y1wVlFNaZ3N3_2-oMqXbUjrQfP9rQ_8/edit"),
                    menu_item(icon="folder", display="Cover Timetable", url="https://docs.google.com/spreadsheets/d/1axTR4lSSjntAvKqd7xeLcvIcTNTKPp7eCgwqSLjCGTA/edit"),
                    menu_item(icon="folder", display="Meeting Minutes", url="https://drive.google.com/drive/folders/0By9YOJwliLtBOHVvNGJTeG9YSE0"),
                    menu_item(icon="folder", display="Reporting Guidelines Semester 1", url="https://docs.google.com/document/d/10f0X0QbC2-buxR9_t8z-X8iWKLe4BPltbjQQ-rCMPrs/edit"),
                   ]
               }),
        button(name="Homeroom", externalid=-9, size="", color="beige", url="notsure", icon="cube", id="",
               context_menu={
                   'items': homeroom_items}),
        button(name="Library", externalid=-9, size="large", color="yellow", url="https://igbis.follettdestiny.com", icon="university", id="",
               context_menu=None),
        button(name="Calendar", externalid=-9, size="", color="peach", url="https://sites.google.com/a/igbis.edu.my/igbis-calendar/", icon="calendar", id="", context_menu=None),
        handbook_button,
        button(name="Community Information", externalid=-9, size="large", color="aqua", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/home", icon="comments-o", id="",
               context_menu={
                   'items': [
                       menu_item(icon="plus-circle", display="Student Directory", url="https://script.google.com/a/macros/igbis.edu.my/s/AKfycbyA_lbYY75Jc9PRwU4T0mdkdp7xdCyPcPsWXjYix33amJcVRnIiTMKxPZnperCDPc9e/exec#Directory/"),
                       menu_item(icon="plus-circle", display="Medical Information", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/medical-info"),
                       menu_item(icon="plus-circle", display="Bulk Email App", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/bulk-email-app"),
                       menu_separator(),
                       menu_item(icon="", display="Add a Daily Notice", url="https://docs.google.com/a/igbis.edu.my/forms/d/1ni0lu4mzVFzHW8PxWyap8iUEYFjOjEi_z_ZjEDJaS-s/viewform"),
                       menu_item(icon="", display="Today's Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/"),
                       menu_item(icon="", display="Search Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/notices-database"),
                       menu_placeholder('mb_grade_teachers')
                   ]}),
        button(name="Music Academy", externalid=-9, size="", color="cyan", url="https://sites.google.com/a/igbis.edu.my/igbis-instrumental-music-academy/home?pli=1", icon="music", id="", context_menu=None),
        button(name="Houses", externalid=-9, size="", color="orange", url="https://sites.google.com/igbis.edu.my/igbhouses/home", icon="home", id="", context_menu=None),
    ]

    elem_teacher_buttons = [
        button(name="ManageBac", externalid=-9, size="large", color="red", url="https://igbis.managebac.com", icon="fire", id="",
               context_menu={
                   'items': [
                    menu_item(icon="user", display="HR Attendance", url="https://igbis.managebac.com/dashboard/attendance"),
                    menu_item(icon="calendar-o", display="Calendar", url="https://igbis.managebac.com/home"),
                    menu_item(icon="file-text-o", display="EE", url="https://igbis.managebac.com/dashboard/projects?type=ee")
                   ],
               }),
        button(name="School Email", externalid=-9, size="", color="blue", url="https://gmail.com", icon="envelope", id="",
               context_menu={
                   'items': [
                    menu_item(icon="pencil", display="Compose", url="https://mail.google.com/mail/u/0/#inbox?compose=new"),
                   ]
               }),
        button(name="Google Drive", externalid=-9, size="large", color="cyan", url="https://drive.google.com", icon="files-o", id="",
               context_menu={
                   'items': [
                    menu_item(icon="folder", display="Whole School", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERMjMtbFUwcWhPUTA"),
                    menu_item(icon="folder", display="Elementary", url="https://drive.google.com/drive/#folders/0B4dUGjcMMMERR1gwQUNDbVA0ZzA/0B4dUGjcMMMERQXRSaVJRS0RrZFk"),
                    menu_item(icon="folder", display="Secondary", url="https://drive.google.com/drive/folders/0B4dUGjcMMMERZ0RDRkhzWk5vdWs"),
                    menu_separator(),
                    menu_item(icon="folder", display="Staff Handbook", url="https://drive.google.com/drive/folders/0B0Hfis2hp8mHfi02cGNQY0E1T09IMk1JLWo2WWtkMUNCbEFzaks3aXFKUzlSSGU3eUQwMWc"),
                    menu_item(icon="folder", display="Policies & Procedures", url="https://drive.google.com/open?id=0B_el10BYGhjLfkd1NmZHa3ZCdUxaRlVTSDVEdjVraHh2S053WEFjZFRSeHdzNldpRmNIZFk"),
                    menu_item(icon="folder", display="CIS/NEASC Accreditation", url="https://drive.google.com/drive/folders/0By9YOJwliLtBM0FxRHFEVWVEcVk"),
                    menu_item(icon="folder", display="Insurance Forms", url="https://drive.google.com/drive/folders/1Nz7s1LLuuZ8VIrjK7mQlojnsxeK0OHrn")
                   ]
               }),
        button(name="Google Plus", externalid=-9, size="", color="green", url="https://plus.google.com/", icon="google-plus", id="", context_menu=None),
        button(name="Library", externalid=-9, size="large", color="yellow", url="https://igbis.follettdestiny.com", icon="university", id="",
               context_menu=None),
        button(name="Calendar", externalid=-9, size="", color="peach", url="https://sites.google.com/a/igbis.edu.my/igbis-calendar/", icon="calendar", id="", context_menu=None),
        handbook_button,

        button(name="Community Information", externalid=-9, size="large", color="aqua", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/home", icon="comments-o", id="", context_menu={
            'items': [
                menu_item(icon="plus-circle", display="Student Directory", url="https://script.google.com/a/macros/igbis.edu.my/s/AKfycbyA_lbYY75Jc9PRwU4T0mdkdp7xdCyPcPsWXjYix33amJcVRnIiTMKxPZnperCDPc9e/exec#Directory/"),
                menu_item(icon="plus-circle", display="Medical Information", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/medical-info"),
                menu_item(icon="plus-circle", display="Bulk Email App", url="https://sites.google.com/igbis.edu.my/oambdatamanagement/bulk-email-app"),
                menu_separator(),
                menu_item(icon="plus-circle", display="Add a Daily Notice", url="https://docs.google.com/a/igbis.edu.my/forms/d/1ni0lu4mzVFzHW8PxWyap8iUEYFjOjEi_z_ZjEDJaS-s/viewform"),
                menu_item(icon="calendar-check-o", display="Today's Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/"),
                menu_item(icon="search", display="Search Notices", url="https://sites.google.com/a/igbis.edu.my/igbis-daily-notices/notices-database")
            ]}),
        button(name="Music Academy", externalid=-9, size="", color="cyan", url="https://sites.google.com/a/igbis.edu.my/igbis-instrumental-music-academy/home?pli=1", icon="music", id="", context_menu=None),
        button(name="Houses", externalid=-9, size="", color="orange", url="https://sites.google.com/igbis.edu.my/igbhouses/home", icon="home", id="", context_menu=None),
    ]

    elem_teacher_buttons.extend([
        button(name="Teacher Dashboard", externalid=-9, size="large", color="purple", url="https://teacherdashboard.appspot.com/igbis.edu.my", icon="dashboard", id="", context_menu=None),
        ibo_button,
        counselor_button_not_students,
        button(name="Reports Hub", externalid=-9, size="", color="orange", url="reports_hub", icon="gavel", id="", context_menu=None),
        button(name="IT Integration", externalid=-9, size="", color="yellow", url="https://sites.google.com/igbis.edu.my/digitalliteracy", icon="arrows", id="", context_menu={
            'items': [
                menu_item(icon="thumb-tack", display="Book Geoff", url="https://geoffreyderry.youcanbook.me/"),
                menu_item(icon="apple", display="Digital Literacy Site", url="https://sites.google.com/igbis.edu.my/digitalliteracy"),
                menu_item(icon="apple", display="IT Committee", url="https://sites.google.com/igbis.edu.my/itcommittee"),
            ]}),
        button(name="Help Desk: IT&nbsp;&amp;&nbsp;Facilities", externalid=-9, size="", color="red", url="http://rodmus.igbis.local/", icon="exclamation-circle", id="", context_menu=None),
        button(name="BrainPop", externalid=-9, size="", color="beige", url="https://www.brainpop.com/user/loginDo.weml?user=igbisbrainpop&password=2014igbis", icon="film", id="", context_menu=None),
        bookings_button,
        button(name="Activities & Athletics", externalid=-9, size="", color="pink", url="https://sites.google.com/igbis.edu.my/athleticsactivities", icon="rocket", id="",
               context_menu=None),
        cashless_button,
        button(name="ES Behaviour Report", externalid=-9, size="", color="purple", url="", icon="bullhorn", id="", context_menu={
            'items': [
                menu_item(icon="thumb-tack", display="Submit Behaviour Report", url="https://goo.gl/forms/ZGX0fyDhSJLtaYz22"),
                menu_item(icon="apple", display="View Behaviour Reports", url="https://sites.google.com/igbis.edu.my/esbehaviourreports/home")
            ]}),
        emergency_procedures,
        box_of_books_button,
        import_my_calendar_button,
        managebac_info_button,
        ib_app_button
    ])

    sec_teacher_buttons.extend([
        button(name="Teacher Dashboard", externalid=-9, size="large", color="purple", url="https://teacherdashboard.appspot.com/igbis.edu.my", icon="dashboard", id="", context_menu=None),
        ibo_button,

        counselor_button_not_students,
        button(name="Activities & Athletics", externalid=-9, size="", color="pink", url="https://sites.google.com/igbis.edu.my/athleticsactivities", icon="rocket", id="",
               context_menu=None),

        button(name="Secondary&ensp;Procedures", externalid=-9, size="", color="peach", icon="trophy", url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal", id="",
               context_menu={
                   'items': [
                       menu_item(icon="pencil", display="Behaviour Report Form", url="https://docs.google.com/a/igbis.edu.my/forms/d/1aTxoKnpGjuY9DcNJ7UlTJ6egsjG8-FMYTLpjvM1jdbY/viewform?c=0&w=1"),
                       menu_item(icon="pencil", display="Absences / Cover", url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/teacher-absences"),
                       menu_item(icon="pencil", display='Professional Development Requests', url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/professional-development"),
                       menu_item(icon="pencil", display='Events at IGBIS', url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/events"),
                       menu_item(icon="pencil", display='Students - Late arrival & Leaving early', url="https://sites.google.com/a/igbis.edu.my/igbis-ssprincipal/late-students"),
                   ]}),

        button(name="My IB", externalid=-9, size="", color="beige", url="https://internationalbaccalaureate.force.com/ibportal/IBPortalLogin", icon="sign-in", id="", context_menu=None),
        button(name="IT Integration", externalid=-9, size="", color="yellow", url="https://sites.google.com/igbis.edu.my/digitalliteracy", icon="arrows", id="", context_menu={
            'items': [
                menu_item(icon="thumb-tack", display="Book Geoff", url="https://geoffreyderry.youcanbook.me/"),
                menu_item(icon="apple", display=" Digital Literacy Site", url="https://sites.google.com/igbis.edu.my/digitalliteracy"),
                menu_item(icon="apple", display="IT Committee", url="https://sites.google.com/igbis.edu.my/itcommittee"),
            ]}),
        button(name="Help Desk: IT&nbsp;&amp;&nbsp;Facilities", externalid=-9, size="", color="red", url="http://rodmus.igbis.local/", icon="exclamation-circle", id="", context_menu=None),
        bookings_button,
        cashless_button,
        emergency_procedures,
        box_of_books_button,
        import_my_calendar_button,
        managebac_info_button,
        ib_app_button,
        personal_project
    ])

    buttons = OrderedDict()

    if logged_in_user:
        account_type = logged_in_user.type
        if account_type == 'Account Admins' or account_type == 'Advisors' or account_type == 'Advisor':
            buttons['Secondary_Teachers'] = sec_teacher_buttons
            buttons['Elementary_Teachers'] = elem_teacher_buttons
            buttons['Students'] = student_buttons
            buttons['Parents'] = parent_buttons
            buttons['Admin'] = administration_buttons
        elif account_type == 'Students':
            buttons['Students'] = student_buttons
            buttons['Parents'] = parent_buttons
        elif account_type == 'Parents':
            buttons['Parents'] = parent_buttons
            buttons['Students'] = student_buttons
        elif account_type == 'BusAdmin':
            buttons['Administration'] = administration_buttons
            buttons['Secondary_Teachers'] = sec_teacher_buttons
            buttons['Elementary_Teachers'] = elem_teacher_buttons
            buttons['Students'] = student_buttons
            buttons['Parents'] = parent_buttons
        else:
            buttons["Welcome_{}".format(account_type)] = parent_buttons
    else:
        buttons['Welcome'] = parent_buttons

    g_plus_unique_id = request.session.get('g_plus_unique_id')
    settings = None
    if g_plus_unique_id:
        with DBSession() as session:
            try:
                settings = session.query(db.table.UserSettings).filter_by(unique_id=g_plus_unique_id).one()
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
        buttons=buttons,
        settings=settings
    )
