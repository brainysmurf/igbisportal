"""
Defines the SQL schema that defines our database.
There are tools out there that will define this automatically, but I don't have access to the database store
So instead I wrote it out by hand

This is based on the API that ManageBac gives, I have found that the API in OpenApply is actually different
for example national_id not = password_number

So I guess we'll have to figure that out if we choose to go to production quality
"""

course_abbreviations = {
    'English Language Acquisition':'ELA',
    'English Language and Literature':'EL&amp;L',
    'Physical and Health Education': 'PSHE',
    'Korean Language and Literature': 'Kor Lang & Lit',
    'Bahasa Malaysia Language and Literature': 'BML&L',
    'Bahasa Malaysia Language Acquisition': 'BMLA',
    'Chinese Langauge and Literature': 'CL&L',
    'Chinese Language Acquisition': 'CLA',
    'Host Nation Studies': 'Host Nations',
    'Spanish Language Acquisition': 'SLA',
    'French Language Acquisition': 'FLA', 
    'Individuals and Societies - Integrated Humanities': "I&amp;S",
}

import unicodedata
def normalize(this_string): 
    return unicodedata.normalize('NFKD', this_string).encode('ascii', 'ignore')

from sqlalchemy import BigInteger, Boolean, Enum, Column, Float, Index, Integer, Numeric, SmallInteger, String, Table, Text, ForeignKey, Date, case, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.functions import concat
from sqlalchemy.sql.expression import case
from sqlalchemy import inspect, func
Base = declarative_base()
metadata = Base.metadata
import datetime
from sqlalchemy.orm import relationship, backref

from collections import defaultdict
import re
from portal.utils import get_year_of_graduation, get_this_academic_year

class EmergInfo:
    def __init__(self, num):
        self.num = num
        self.relationship = ""
        self.email_address = ""
        self.first_name = ""
        self.last_name = ""
        self.telephone = ""

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return "({}) {} {} {}".format(self.num, self.name, self.relationship, self.telephone, self.email_address)

"""
Klunky, but lets me debug quickly
"""
import gns
PREFIX = gns.config.database.prefix
if PREFIX is None or PREFIX.upper() is "NONE":
    PREFIX = ""
TABS = "{}tabs".format(PREFIX)
BUTTONS = "{}buttons".format(PREFIX)
SUBMENUS = "{}submenus".format(PREFIX)
SPLASHJSON = "{}splash_jsons".format(PREFIX)
USERS = "{}users".format(PREFIX)
STUDENTS = "{}students".format(PREFIX)
PARENTS = "{}parents".format(PREFIX)
ADVISORS = "{}teachers".format(PREFIX)
COURSES = "{}courses".format(PREFIX)
BUSADMIN = "{}busadmin".format(PREFIX)
PARENTCHILDREN = "{}parentchildren".format(PREFIX)
ASSIGNMENT = "{}assignment".format(PREFIX)
ENROLLMENT = "{}enrollment".format(PREFIX)
TIMETABLES = "{}timetables".format(PREFIX)
IBGROUPS = "{}ibgroups".format(PREFIX)
IBGROUPSMEMBERSHIP = "{}ibgroupsmembership".format(PREFIX)
AUDITLOGS = "{}auditlogs".format(PREFIX)
TERMS = "{}terms".format(PREFIX)
REPORTCOMMENTS = "{}report_comments".format(PREFIX)
ATLCOMMENTS = "{}atl_comments".format(PREFIX)
REPORTATLASSOC = "{}report_atl_association".format(PREFIX)
PRIMARYREPORT = "{}primary_report".format(PREFIX)
PRIMARYREPORTSECTION = "{}primary_report_section".format(PREFIX)
PRIMARYREPORTSTRAND = "{}primary_report_strand".format(PREFIX)
PRIMARYREPORTLO = "{}primary_report_lo".format(PREFIX)
PRIMARYREPORTSECTIONTEACHERASSOC = "{}primary_report_section_teacher_association".format(PREFIX)
PYPTEACHERASSIGNMENTS = "{}primary_teacher_assign".format(PREFIX)
PYPSTUDENTABSENCES = "{}primary_student_absences".format(PREFIX)
SECHRTEACHERS = "{}sec hr teachers".format(PREFIX)
SETTINGS = "{}settings".format(PREFIX)
MEDINFO = "{}medinfo".format(PREFIX)

class PortalORM(object):
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_array(self):
        ret = []
        for column in range(len(self.__table__.columns)):
            ret[column] = getattr(self, self.__table__.columns[column])
        return ret

    @classmethod
    def columns_and_hybrids(cls, filter_out=None):
        """
        FIXME: This doesn't seem to be working
        filter_out TODO make it so that you can define a lambda
        """
        insp = inspect(cls)
        column_attrs = [c.name for c in insp.columns]
        column_attrs.extend( [item.__name__ for item in insp.all_orm_descriptors if item.extension_type is HYBRID_PROPERTY and item.__name__ != '<lambda>'] )
        column_attrs.sort()
        return column_attrs

    @classmethod
    def hybrids(cls, filter_out=None):
        """
        FIXME: This doesn't seem to be working
        filter_out TODO make it so that you can define a lambda
        """
        insp = inspect(cls)
        #column_attrs = [c.name for c in insp.columns]
        column_attrs = [item.__name__ for item in insp.all_orm_descriptors if item.extension_type is HYBRID_PROPERTY and item.__name__ != '<lambda>']
        column_attrs.sort()
        return column_attrs

    @property
    def columns_hybrids_dict(self):
        insp = inspect(self.__class__)
        column_attrs = [c.name for c in insp.columns]
        column_attrs.extend( [item.__name__ for item in insp.all_orm_descriptors if item.extension_type is HYBRID_PROPERTY and item.__name__ != '<lambda>'] )
        column_attrs.sort()
        d = {}
        for column in column_attrs:
            d[column] = getattr(self, column)
        return d

class UserSplashJson(Base):
    __tablename__ = SPLASHJSON
    id = Column(String, primary_key=True)
    json = Column(Text)

# class UserDefinedTabs(Base):
#     __tablename__ = TABS
#     id = Column(BigInteger, primary_key=True)
#     name = Column(String)
#     g_plus_unique_id = Column(String)
#     buttons = relationship("UserDefinedButtons")

# class UserDefinedButtons(Base):
#     __tablename__ = BUTTONS
#     id = Column(BigInteger, primary_key=True)
#     externalid = Column(BigInteger)
#     name = Column(String)
#     color = Column(String)
#     icon = Column(String)
#     size = Column(Integer)
#     url = Column(String)
#     tab = Column(Integer, ForeignKey(TABS+'.id'))
#     context_menu = relationship("UserDefinedSubMenus")

# class UserDefinedSubMenus(Base):
#     __tablename__ = SUBMENUS
#     id = Column(BigInteger, primary_key=True)
#     name = Column(String)
#     url = Column(String)    
#     button = Column(Integer, ForeignKey(BUTTONS+'.id'))

class User(PortalORM):
    """
    Fields shared by all users
    TODO: Check this more carefully, bound to need some tweaks
    """
    type = Column(String(255))

    domain = '@igbis.edu.my'

    first_name = Column(String(255))
    last_name = Column(String(255))

    gender = Column(String(255))

    national_id = Column(String(255))   # This is the same as passport ID??  Fix
    email = Column(String(255))

    nationality1 = Column(String(255))
    nationality2 = Column(String(255))
    nationality3 = Column(String(255))
    nationality4 = Column(String(255))
    language1 = Column(String(255))
    language2 = Column(String(255))
    language3 = Column(String(255))
    language4 = Column(String(255))

    phone_number = Column(String(255))
    mobile_phone_number = Column(String(255))

    street_address = Column(String(255))
    street_address_ii = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    zipcode = Column(String(255))

    g_plus_unique_id = Column(String(255))

    igbid = Column(BigInteger)

    @property
    def kind(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return (self.first_name or "") + ' ' + (self.last_name or "")

    @property
    def is_male(self):
        return self.gender == 'Male'

    @property
    def is_female(self):
        return self.gender == 'Female'

    @hybrid_property
    def gender_abbrev(self):
        return "M" if self.is_male else ("F" if self.is_female else "<unknown>")

    @gender_abbrev.expression
    def gender_abbrev_expression(cls):
        return case([
                (cls.gender == "Male", "M"),
                (cls.gender == "Female", "F")
            ],
            else_ = "<unknown gender>")

    @hybrid_property
    def username(self):
        return self.email.split("@")[0] if "@" in self.email else ""

    @username.expression
    def username_expression(cls):
        return func.split_part(cls.email, "@", 1)

    @hybrid_property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @full_name.expression
    def full_name_expression(cls):
        return concat(cls.first_name, " ", cls.last_name)

class BusAdmin(Base, User):
    __tablename__ = BUSADMIN
    id = Column(BigInteger, primary_key=True)

class Users(Base, User):
    """
    The basic user information
    """
    __tablename__ = USERS
    id = Column(BigInteger, primary_key=True)

    def __repr__(self):
        return '<User ({})>'.format(self.id)

    def __str__(self):
        return '<User ({})>'.format(self.id)

"""
Many to many relationships need an association table, this is it for parent/children links
"""
ParentChildren = Table(
    PARENTCHILDREN, Base.metadata,
    Column('parent_id', BigInteger, ForeignKey(PARENTS+'.id'), primary_key=True),
    Column('student_id', BigInteger, ForeignKey(STUDENTS+'.id'), primary_key=True)
    )

"""
Many to many relationships need an association table, this is it for teacher/course links
TODO: Haven't checked if this is working and/or correct
"""
Assignment = Table(
    ASSIGNMENT, Base.metadata,
    Column('course_id', BigInteger, ForeignKey(COURSES+'.id'), primary_key=True),
    Column('teacher_id', BigInteger, ForeignKey(ADVISORS+'.id'), primary_key=True)
    )

"""
Many to many relationships need an association table, this is it for student/course links
"""
Enrollment = Table(
    ENROLLMENT, Base.metadata,
    Column('course_id', BigInteger, ForeignKey(COURSES+'.id'), primary_key=True),
    Column('student_id', BigInteger, ForeignKey(STUDENTS+'.id'), primary_key=True)
    )

"""
Many to many relationships need an association table, this is it for IBGroups/members links
TODO: Wait, can a user be a member of only one IB Group?
"""
IBGroupMembership = Table(
    IBGROUPSMEMBERSHIP, Base.metadata,
    Column('ib_group_id', BigInteger, ForeignKey(IBGROUPS+'.id'), primary_key=True),
    Column('student_id', BigInteger, ForeignKey(STUDENTS+'.id'), primary_key=True)
    )

class Student(Base, User):
    """
    I am a student in ManageBac
    """
    __tablename__ = STUDENTS

    id = Column(BigInteger, primary_key=True)

    student_id = Column(String(255))
    program = Column(String(255))
    class_year = Column(Integer)
    class_grade = Column(String)
    archived = Column(Boolean)

    nickname = Column(String(255))

    parents = relationship('Parent', secondary=ParentChildren, backref='children')

    classes = relationship('Course', secondary=Enrollment, backref='students')
    ib_groups = relationship('IBGroup', secondary=IBGroupMembership, backref='students')

    language = Column(String(255))   # only one with language and not languageX  HUH

    attendance_start_date = Column(String(255))
    birthday = Column(String(255))

    open_apply_student_id = Column(String(255))
    homeroom_advisor = Column(BigInteger, ForeignKey(ADVISORS+'.id'))

    profile_photo = Column(String(1000))

    status = Column(String(255))

    def __repr__(self):
        return '<Student {}>'.format(self.first_nickname_last_studentid)

    def __str__(self):
        return "<Student {}>".format(self.first_nickname_last_studentid)

    @hybrid_property
    def start_date(self):
        """
        Python date object of when the student starts school
        """
        str_value = self.attendance_start_date
        if not str_value:
            return None
        return datetime.datetime.strptime(str_value, '%Y-%M-%d')

    @start_date.expression
    def start_date_expression(cls):
        return func.to_timestamp(cls.attendance_start_date, "YYYY-MM-DD")

    @hybrid_property
    def is_archived(self):
        return bool(self.archived)

    @is_archived.expression
    def is_archived_expression(cls):
        return case([
                (cls.archived == True, True),
                (cls.archived == False, False)
            ],
            else_ = False)

    @hybrid_property
    def year_of_graduation(self):
        grade = self.grade
        if grade == -10:
            return -10
        # calculate the year of graduation
        return get_year_of_graduation(grade)

    @hybrid_property
    def parent_emails(self):
        ret = []
        for parent in self.parents:
            ret.append(parent.email)
        return ",".join(set(ret))

    # TODO: I never figured this out, but probably not worh the effort
    # @parent_emails.expression
    # def parent_emails_expression(cls):
    #     return select([Parent.email]).\
    #         join(ParentChildren, ParentChildren.student_id == cls.id).\
    #         join(Parent, Parent.id == ParentChildren.parent_id)

    @hybrid_property
    def parent_names(self):
        ret = []
        for parent in self.parents:
            ret.append(parent.name)
        return ",".join(set(ret))

    @hybrid_property
    def parent_name_1(self):
        parents = self.parents
        if len(parents) > 0:
            parent = parents[0]
            return parent.name
        return ""

    @hybrid_property
    def parent_name_2(self):
        parents = self.parents
        if len(parents) > 1:
            parent = parents[1]
            return parent.name
        return ""

    @hybrid_property
    def parent_email_1(self):
        parents = self.parents
        if len(parents) > 0:
            parent = parents[0]
            return parent.email
        return ""

    @hybrid_property
    def parent_work_email_1(self):
        parents = self.parents
        if len(parents) > 0:
            parent = parents[0]
            return parent.work_email
        return ""

    @hybrid_property
    def parent_email_2(self):
        parents = self.parents
        if len(parents) > 1:
            parent = parents[1]
            return parent.email
        return ""

    @hybrid_property
    def parent_work_email_2(self):
        parents = self.parents
        if len(parents) > 1:
            parent = parents[1]
            return parent.email
        return ""

    @hybrid_property
    def parent_contact_info(self):
        s = ""
        for p in range(len(self.parents)):
            parent = self.parents[p]
            s += "({}) {} {} {} {} {} {} ".format(p+1, parent.name or "", parent.email or "", parent.phone_number or "", parent.mobile_phone_number or "", parent.street_address or "", parent.street_address_ii or "")
        return s

    @hybrid_property
    def program_of_study(self):
        return ", ".join([g.program.upper() for g in self.ib_groups])

    @hybrid_property
    def teacher_emails(self):
        lst = []
        for course in self.classes:
            for teacher in course.teachers:
                lst.append(teacher.email.lower())
        return ",".join(set(lst))

    @hybrid_property
    def teacher_usernames(self):
        lst = []
        for course in self.classes:
            for teacher in course.teachers:
                lst.append(teacher.username_handle.lower())
        return ",".join(set(lst))

    @hybrid_property
    def teacher_names(self):
        lst = []
        for course in self.classes:
            for teacher in course.teachers:
                lst.append(teacher.first_name + ' ' + teacher.last_name)
        return ", ".join(lst)

    @hybrid_property
    def nickname_last_studentid(self):
        return (self.nickname + ' ' + self.last_name + ' (aka ' + self.first_name + ')' if self.nickname and self.nickname != self.first_name else self.first_name + ' ' + self.last_name) + ' [' + str(self.student_id) + ']'

    @hybrid_property
    def last_first_nickname_studentid(self):
        return self.last_name + ', ' + self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') + ' [' + str(self.student_id) + ']'

    @hybrid_property
    def grade_last_first_nickname_studentid(self):
        return str(self.abbrev_grade) + ': ' + self.last_name + ', ' + self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') + ' [' + str(self.student_id) + ']'

    @hybrid_property
    def first_nickname_last_studentid(self):
        return normalize(self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') + ' ' + self.last_name + ' [' + str(self.student_id) + ']')

    @first_nickname_last_studentid.expression
    def first_nickname_last_studentid(cls):
        return cls.first_name + (' (' + cls.nickname + ')' if cls.nickname and cls.nickname != cls.first_name else '') + ' ' + cls.last_name + ' [' + str(cls.student_id) + ']'

    @hybrid_property
    def first_nickname_last(self):
        return self.first_nickname + u' ' + self.last_name

    @hybrid_property
    def first_nickname(self):
        return self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else u'')

    @hybrid_property
    def grade_first_nickname_last_studentid(self):
        return str(self.abbrev_grade) + ': ' + self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') + ' ' + self.last_name + ' [' + str(self.student_id) + ']'

    @hybrid_property
    def grade(self):
        return {
                'Grade 12':12, 
                'Grade 11':11, 
                'Grade 10':10, 
                'Grade 9': 9, 
                'Grade 8': 8, 
                'Grade 7': 7, 
                'Grade 6': 6, 
                'Grade 5': 5, 
                'Grade 4': 4, 
                'Grade 3': 3, 
                'Grade 2': 2, 
                'Grade 1': 1, 
                'Fireflies': -3,
                'Early Years 1':-2, 
                'Early Years 2':-1, 
                'Kindergarten': 0,
            }.get(self.class_grade, -10)

    @grade.expression
    def grade_expression(cls):
        return case([
                (cls.class_grade == 'Fireflies', -3), 
                (cls.class_grade == 'Early Years 1', -2), 
                (cls.class_grade == 'Early Years 2', -1), 
                (cls.class_grade == 'Kindergarten', 0), 
                (cls.class_grade == 'Grade 1', 1), 
                (cls.class_grade == 'Grade 2', 2), 
                (cls.class_grade == 'Grade 3', 3), 
                (cls.class_grade == 'Grade 4', 4), 
                (cls.class_grade == 'Grade 5', 5), 
                (cls.class_grade == 'Grade 6', 6), 
                (cls.class_grade == 'Grade 7', 7), 
                (cls.class_grade == 'Grade 8', 8), 
                (cls.class_grade == 'Grade 9', 9), 
                (cls.class_grade == 'Grade 10', 10), 
                (cls.class_grade == 'Grade 11', 11), 
                (cls.class_grade == 'Grade 12', 12),
            ],
            else_ = -10)

    @hybrid_property
    def grade_range(self):
        if self.grade in range(-5, 0):
            return 1
        if self.grade in range(0, 3):
            return 10
        if self.grade in range(3, 6):
            return 100
        if self.grade in range(6, 9):
            return 1000
        if self.grade in range(9, 13):
            return 10000

    @hybrid_property
    def abbrev_grade(self):
        return {
                'Grade 12':'12', 
                'Grade 11':'11', 
                'Grade 10':'10', 
                'Grade 9': '9', 
                'Grade 8': '8', 
                'Grade 7': '7', 
                'Grade 6': '6', 
                'Grade 5': '5', 
                'Grade 4': '4', 
                'Grade 3': '3', 
                'Grade 2': '2', 
                'Grade 1': '1', 
                'Early Years 1':'EY1', 
                'Early Years 2':'EY2',
                'Kindergarten': 'KG',
                'Fireflies': 'FF',
            }.get(self.class_grade, '<ng>')

    @abbrev_grade.expression
    def abbrev_grade_expression(cls):
        return case([
                (cls.class_grade == 'Fireflies', 'FF'), 
                (cls.class_grade == 'Early Years 1', 'EY1'), 
                (cls.class_grade == 'Early Years 2', 'EY2'), 
                (cls.class_grade == 'Kindergarten', 'KG'), 
                (cls.class_grade == 'Grade 1', '1'), 
                (cls.class_grade == 'Grade 2', '2'), 
                (cls.class_grade == 'Grade 3', '3'), 
                (cls.class_grade == 'Grade 4', '4'), 
                (cls.class_grade == 'Grade 5', '5'), 
                (cls.class_grade == 'Grade 6', '6'), 
                (cls.class_grade == 'Grade 7', '7'), 
                (cls.class_grade == 'Grade 8', '8'), 
                (cls.class_grade == 'Grade 9', '9'), 
                (cls.class_grade == 'Grade 10', '10'), 
                (cls.class_grade == 'Grade 11', '11'), 
                (cls.class_grade == 'Grade 12', '12'),
            ],
            else_ = -10)

    @hybrid_property
    def health_information(self):
        from portal.db import DBSession, Database
        db = Database()
        from sqlalchemy.orm.exc import NoResultFound
        MedInfo = db.table_string_to_class('med_info')

        with DBSession() as session:
            try:
                med_info = session.query(MedInfo).filter_by(id=self.id).one()
            except NoResultFound:
                return "<>"

            return med_info.health_information

    @hybrid_property
    def emergency_info(self):
        from portal.db import DBSession, Database
        db = Database()
        from sqlalchemy.orm.exc import NoResultFound
        MedInfo = db.table_string_to_class('med_info')

        with DBSession() as session:
            try:
                med_info = session.query(MedInfo).filter_by(id=self.id).one()
            except NoResultFound:
                return "<>"

            return med_info.emergency_info

    @hybrid_property
    def homeroom_teacher_email(self):
        return self.homeroom_teacher.email if self.homeroom_teacher else "<unknown hr teacher>"

    @homeroom_teacher_email.expression
    def homeroom_teacher_email_expression(cls):
        return Advisor.email

    @hybrid_property
    def homeroom_abbrev(self):
        """
        TODO: This is very make-shift
        """
        homeroom_mapping = {
            'rachel.fleury':(6, '6'),
            'tim.bartle': (7, '7'),
            'sheena.kelly': (7, '7'), 
            'benjamin.wylie': (8, '8'),
            'emily.heys': (8, '8'),
            'dean.watters':(9, '9'),
            'glen.fleury': (9, '9'),
            'marcus.wetherell': (10, '10'),
            'diane.douglas': (10, '10'),
            'paul.skadsen': (11, '11'),
            'nathalie.chotard': (11, '11'),
            'gabriel.evans': (11, '11'),
            'michael.hawkes': (12, '12'),
            'mary.richards': (-9, 'EY{}R'),
            'deborah.king': (-9, 'EY{}K'),
            'sally.watters': (-9, 'EY{}W'),
            'leanne.harvey':(0, 'KH'),
            'lisa.mcclurg': (0, 'KM'),
            'shireen.blakeway': (1, '1B'),
            'kath.kummerow': (2, '2K'),
            'michelle.ostiguy': (3, '3O'),
            'marshall.hudson': (3, '3H'),
            'kari.twedt': (4, '4T'),
            'steven.harvey': (4, '4H'),
            'kathy.mckenzie': (5, '5M'),
            'yolaine.johanson': (5, '5J'),
            }
        if not self.homeroom_teacher:
            return "<HR>"
        username = self.homeroom_teacher.username_handle
        grade, homeroom = homeroom_mapping.get(username, (None, None))
        if grade is None or homeroom is None:
            return "<HR?>"
        if grade >= 6:
            return "{}{}".format(self.grade, (self.homeroom_teacher.username_handle.split('.')[1][0]).upper())
        elif grade == 0:
            return homeroom
        elif grade >= -2:
            return "{}{}".format(self.grade, homeroom)
        elif grade == -9:
            grad_year = self.year_of_graduation
            this_year = 2000 + get_this_academic_year()
            if grad_year - this_year == (12 + 2):
                # early years 1
                return homeroom.format(1)
            elif grad_year - this_year == (12 + 1): 
                # early years 2
                return homeroom.format(2)

    @hybrid_property
    def homeroom_full(self):
        """
        TODO: This is very make-shift
        """
        if not self.homeroom_teacher:
            return "<no hr teacher>"
        return {
            'jade.saba': 'Grade 6S',
            'sheena.kelly': 'Grade 6K', 
            'glen.fleury': 'Grade 7F',
            'jo.spivey-jones': 'Grade 7S',
            'adam.morris': 'Grade 8M',
            'silvana.evans': 'Grade 8E',
            'mick.smith': 'Grade 9M',
            'dean.watters': 'Grade 9W',
            'marcus.wetherell': 'Grade 10W',
            'scott.cameron': 'Grade 10C',
            'diane.douglas': 'Grade 11D',
            'matthew.marshall': 'Grade 11M',
            'christopher.thompson': 'Grade 12T',
            'nathalie.chotard': 'Grade 12C',
            'mary.richards': 'Early Years 1/2R',
            'tamara.snooks': 'Early Years 1/2S',
            'deborah.king': 'Early Years 1/2K',
            'leanne.harvey': 'Kindergarden H',
            'megan.ngatai':  'Kindergarden N',
            'shireen.blakeway': 'Grade 1B',
            'sally.watters': 'Grade 1W',
            'stephanie.wafzig': 'Grade 2W',
            'clare.demnar': 'Grade 2D',

            'lisa.mcclurg': 'Grade 3M',
            'marshall.hudson': 'Grade 3H',

            'kari.twedt': 'Grade 4T',
            'steven.harvey': 'Grade 4H',

            'yolaine.johanson': 'Grade 5J',
            'kathy.mckenzie': 'Grade 5M',
            }.get(self.homeroom_teacher.username_handle.lower(), '<unknown>')

    @hybrid_property
    def barcode(self):
        return 'P {}'.format(self.student_id) 

    @hybrid_property
    def destiny_site_information(self):
        return {
            'PYP': "IGBISE",
            'MYP': "IGBISS",
            'DIPLOMA': "IGBISS"
        }.get(self.program_of_study, "<unknown site>")

    @hybrid_property
    def destiny_patron_type(self):
        if self.grade in range(6,11):
            return "Student G6-G10"
        elif self.grade in range(11,13):
            return "Student G11-G12"
        elif self.grade in range(0, 3):
            return "Student K-2"
        elif self.grade in range(3, 6):
            return "Student Grade 3-5"
        elif self.grade in range(-2,0):
            return "Early Years (EY1-EY2)"
        elif self.grade == -3:
            return "Fireflies"
        else:
            return "<unknown program>"

class Parent(Base, User):
    """
    I am a parent in ManageBac

    TODO: Create some glue code that makes a 'work_info' Many-to-one relation
    """
    __tablename__ = PARENTS

    id = Column(BigInteger, primary_key=True)

    nickname = Column(String(255))
    salutation = Column(String(255))

    employer = Column(String(255))
    title = Column(String(255))

    openapply_parent_id = Column(String(255))
    openapply_student_id = Column(String(255))

    # children relation made by Student.parents 'backref'

    # FIXME: This is crazy, why define the work info for each parent??
    work_street_address = Column(String(255))
    work_street_address_ii = Column(String(255))
    work_city = Column(String(255))
    work_state = Column(String(255))
    mobile_phone = Column(String(255))
    home_phone = Column(String(255))
    work_phone = Column(String(255))
    work_email = Column(String(255))

    @hybrid_property
    def igbis_username(self):
        return "{}.{}.parent".format(re.sub('[^0-9a-z]', '', self.first_name.replace(' ', '').lower()), re.sub('[^0-9a-z]', '', self.last_name.replace(' ', '').lower()))

    @hybrid_property
    def igbis_email_address(self):
        return self.igbis_username + '@igbis.edu.my'

    @igbis_username.expression
    def igbis_username_expression(cls):
        return func.lower(func.regexp_replace(func.concat(cls.first_name, '.', cls.last_name, '.parent'), '[^0-9A-Za-z.]', ''))

    @igbis_email_address.expression
    def igbis_email_address_expression(cls):
        return func.concat(cls.igbis_username_expression, cls.domain)

    @hybrid_property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @hybrid_property
    def first_child_date_started(self):
        """
        Returns date object of student who started first
        """
        earliest = None
        for child in self.children:
            this_date = child.start_date
            if not this_date:
                continue
            if earliest is None or this_date < earliest:
                earliest = this_date
        return earliest

    def google_account_sunset(self, duration):
        """
        Return true if this account has been around long enough for them to convert using this domain
        TODO: Consider putting this in another layer
        TODO: string interface used for duration could be in a utils function

        @duration string representing how long '1 week, 3 weeks, 3 months'
        """
        earliest = self.first_child_date_started
        if earliest is None:
            # what do I do?
            print(self)
            return

        dur = {
                '3 weeks': datetime.timedelta(weeks=3),
                '2 weeks': datetime.timedelta(weeks=2),
                '1 week': datetime.timedelta(weeks=1),
                '3 months': datetime.timedelta(weeks=4*3),
                '2 months': datetime.timedelta(weeks=4*2),
                '1 month': datetime.timedelta(weeks=4)
            }\
            .get(duration.strip().lower(), None)

        ret = datetime.datetime.now() > earliest
        return ret

    def __repr__(self):
        return '<Parent ({}) '.format(self.id) + self.name + '>'

    def __str__(self):
        return '<Parent ({}) '.format(self.id) + self.name + '>'


class Advisor(Base, User):
    """
    I am a teacher in ManageBac, obviously we call them advisors for legacy reasons
    """

    __tablename__ = ADVISORS

    id = Column(BigInteger, primary_key=True)

    first_name = Column(String(255))
    last_name = Column(String(255))
    national_id = Column(String(255))
    classes = relationship('Course', secondary=Assignment, backref='teachers')
    homeroom_students = relationship('Student', backref="homeroom_teacher")

    @hybrid_property
    def username_handle(self):
        u, _ = self.email.split('@')
        return u.lower()

    @username_handle.expression
    def username_handle_expression(self):
        return func.lower(func.regexp_replace(self.email, '@.*$', ''))

    @hybrid_property
    def grades_taught(self):
        ret = []
        for class_ in self.classes:
            ret.append(class_.grade)
        return ",".join(set(ret))

    @hybrid_property
    def name(self):
        return self.first_name + ' ' + self.last_name

class Course(Base):
    """
    I am a course/class in ManageBac (class is a reserved word in Python)
    Includes timetable / period information
    """
    __tablename__ = COURSES

    id = Column(BigInteger, primary_key=True)
    type = Column(String(255))
    name = Column(String(255))
    grade = Column(String(255))
    uniq_id = Column(String(255), nullable=True, server_default=None)

    @hybrid_property
    def abbrev_name(self):
        pattern = re.compile(r'\b(' + '|'.join(course_abbreviations.keys()) + r')\b')
        return pattern.sub(lambda x: course_abbreviations[x.group()], self.name)

    # timetables relation defined by Timetable.course 'backref'
    def __repr__(self):
        return '<Class ({}) '.format(self.id) + self.abbrev_name + '>'

    def __str__(self):
        return '<Class ({}) '.format(self.id) + self.abbrev_name + '>'

class Timetable(Base):
    """
    Composite primary key consisting of course_id (ForeignKey) and day and period info
    """
    __tablename__ = TIMETABLES

    course_id = Column(BigInteger, ForeignKey(COURSES+'.id'), primary_key=True)
    day = Column(Integer, primary_key=True)
    period = Column(Integer, primary_key=True)

    course = relationship('Course', backref='timetables')

    def __str__(self):
        return str(self.day) + ': ' + str(self.period)


class IBGroup(Base):
    """
    I am an IBGroup in ManageBac
    """
    __tablename__ = IBGROUPS

    id = Column(BigInteger, primary_key=True)

    grade = Column(String(255))
    program = Column(String(255))
    name = Column(String(255))
    unique_id = Column(String(255))

    def __repr__(self):
        return '<IBGroup ({}) '.format(self.id) + self.name + 'in ' + self.program + '>'

    def __str__(self):
        return '<IBGroup ({}) '.format(self.id) + self.name + 'in ' + self.program + '>'


class SecondaryHomeroomTeachers(Base):
    __tablename__ = SECHRTEACHERS

    id = Column(BigInteger, primary_key=True)

    student_id = Column(BigInteger, ForeignKey(STUDENTS+'.id'))
    teacher_id = Column(BigInteger, ForeignKey(ADVISORS+'.id'))

class AuditLog(Base):
    __tablename__ = AUDITLOGS
    id = Column(BigInteger, primary_key=True)
    date = Column(String(255))
    target = Column(String(255))
    administrator = Column(String(255))
    applicant = Column(String(255))
    action = Column(String(1000))

class Terms(Base):
    """
    TODO: What about academic start date?
    """
    __tablename__ = TERMS

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    start_date = Column(String(255), nullable=True,     server_default=None)
    end_date = Column(String(255))
    current = Column(Boolean, default=False, server_default=None)

comments_association_table = Table(REPORTATLASSOC, Base.metadata,
    Column('report_comment_id', BigInteger, ForeignKey(REPORTCOMMENTS + '.id'), primary_key=True),
    Column('atl_comment_id', BigInteger, ForeignKey(ATLCOMMENTS + '.id'), primary_key=True)
)

class ReportComments(Base):
    __tablename__ = REPORTCOMMENTS

    id = Column(BigInteger, primary_key=True)

    course_id = Column(BigInteger, ForeignKey(COURSES+'.id'))
    course = relationship('Course', uselist=False)
    term_id = Column(BigInteger, ForeignKey(TERMS+'.id'))
    term = relationship('Terms', uselist=False)
    student_id = Column(BigInteger, ForeignKey(STUDENTS+'.id'))
    student = relationship('Student', backref="reports", uselist=False)  # userlist makes it just one

    text = Column(String(1000))

    # One to one? One to many? Who knows.
    teacher_id = Column(BigInteger, ForeignKey(ADVISORS+'.id'))
    teacher = relationship('Advisor')

    atl_comments = relationship('AtlComments', secondary=comments_association_table,
                    backref="reports")

class AtlComments(Base):
    __tablename__ = ATLCOMMENTS
    id = Column(BigInteger, primary_key=True)
    label = Column(Enum('Collaboration', 'Communication', 'Organization', 'Affective', 'Reflection', 'Information Literacy', 'Media Literacy', 'Critical Thinking', 'Creative Thinking', 'Transfer' , name='alt_skills'))
    selection = Column(Enum('EE', 'ME', 'AE', 'BE', name = 'selection'))


class PrimaryReport(Base):
    __tablename__ = PRIMARYREPORT

    id = Column(BigInteger, primary_key=True)   # TODO Use Composite Key?

    course_id = Column(BigInteger, ForeignKey(COURSES+'.id'))
    course = relationship('Course', uselist=False)
    term_id = Column(BigInteger, ForeignKey(TERMS+'.id'))
    term = relationship('Terms', uselist=False)
    student_id = Column(BigInteger, ForeignKey(STUDENTS+'.id'))
    student = relationship('Student', backref="pyp_reports", uselist=False)  # userlist makes it just one

    # One to one? One to many? Who knows.
    teacher_id = Column(BigInteger, ForeignKey(ADVISORS+'.id'))
    teacher = relationship('Advisor')
    sections = relationship('PrimaryReportSection')

    homeroom_comment = Column(String(2000))

    #section = relationship('PrimaryReportSection')

primary_report_section_teacher_association = Table(PRIMARYREPORTSECTIONTEACHERASSOC, Base.metadata,
    Column('primary_report_section_id', BigInteger, ForeignKey(PRIMARYREPORTSECTION+'.id')),
    Column('teacher_id', BigInteger, ForeignKey(ADVISORS+'.id'))
    )

class PrimaryReportSection(Base):
    __tablename__ = PRIMARYREPORTSECTION

    id = Column(BigInteger, primary_key=True)   # TODO Use Composite Key?

    primary_report_id = Column(ForeignKey(PRIMARYREPORT + '.id'))
    subject_id = Column(BigInteger)

    name = Column(String(500))
    comment = Column(String(2000))
    
    teachers = relationship('Advisor', secondary=primary_report_section_teacher_association)
    strands = relationship('PrimaryReportStrand')
    learning_outcomes = relationship('PrimaryReportLo')


class PrimaryReportStrand(Base):
    __tablename__ = PRIMARYREPORTSTRAND
    id = Column(BigInteger, primary_key=True)
    primary_report_section_id = Column(ForeignKey(PRIMARYREPORTSECTION + '.id'))
    which = Column(Integer)

    label = Column(String(1000))
    label_titled = Column(String(1000))
    selection = Column(String(4))
    #selection = Column(Enum('', 'W', 'S', 'I', 'E', name = 'selection'))

class PrimaryReportLo(Base):
    __tablename__ = PRIMARYREPORTLO
    id = Column(BigInteger, primary_key=True)
    primary_report_section_id = Column(ForeignKey(PRIMARYREPORTSECTION + '.id'))
    which = Column(Integer)

    heading = Column(String(1000))  
    label = Column(String(1000))
    label_titled = Column(String(1000))
    selection = Column(String(4))
    #selection = Column(Enum('', 'O', 'G', 'N', name = 'selection'))

class PrimaryTeacherAssignments(Base):
    __tablename__ = PYPTEACHERASSIGNMENTS
    id = Column(BigInteger, primary_key=True)
    teacher_id = Column(ForeignKey(ADVISORS + '.id'))
    subject_id = Column(BigInteger)
    class_id = Column(ForeignKey(COURSES + '.id'))

class PrimaryStudentAbsences(Base):
    __tablename__ = PYPSTUDENTABSENCES
    id = Column(BigInteger, primary_key=True)
    student_id = Column(ForeignKey(STUDENTS + '.id'))
    term_id = Column(ForeignKey(TERMS + '.id'))
    absences = Column(Integer)
    total_days = Column(Integer)

class GoogleSignIn(Base):
    __tablename__ = "GoogleSignIn"   # NOT based on the prefix...

    id = Column(BigInteger, primary_key=True)
    unique_id = Column(String(1000))
    auth_code = Column(String(255))
    access_token = Column(String(255))
    refresh_token = Column(String(255))
    igbid = Column(BigInteger)

class UserSettings(Base):
    __tablename__ = SETTINGS

    id = Column(BigInteger, primary_key=True)
    unique_id = Column(String(255))
    icon_size = Column(String(2))
    new_tab = Column(Boolean)

class MedInfo(Base):
    __tablename__ = MEDINFO

    id = Column(BigInteger, ForeignKey(STUDENTS+'.id'), primary_key=True)

    emergency_contact_1_ec_relationship = Column(String(255))
    emergency_contact_1_email = Column(String(255))
    emergency_contact_1_email_address = Column(String(255))
    emergency_contact_1_first_name = Column(String(255))
    emergency_contact_1_last_name = Column(String(255))
    emergency_contact_1_prefix = Column(String(255))
    emergency_contact_1_relationship = Column(String(255))
    emergency_contact_1_telephone = Column(String(255))
    emergency_contact_1_title = Column(String(255))
    emergency_contact_10_email_address = Column(String(255))
    emergency_contact_10_first_name = Column(String(255))
    emergency_contact_10_last_name = Column(String(255))
    emergency_contact_10_relationship = Column(String(255))
    emergency_contact_10_telephone = Column(String(255))
    emergency_contact_11_email_address = Column(String(255))
    emergency_contact_11_first_name = Column(String(255))
    emergency_contact_11_last_name = Column(String(255))
    emergency_contact_11_relationship = Column(String(255))
    emergency_contact_11_telephone = Column(String(255))
    emergency_contact_12_email_address = Column(String(255))
    emergency_contact_12_first_name = Column(String(255))
    emergency_contact_12_last_name = Column(String(255))
    emergency_contact_12_relationship = Column(String(255))
    emergency_contact_12_telephone = Column(String(255))
    emergency_contact_2_ec_relationship = Column(String(255))
    emergency_contact_2_email = Column(String(255))
    emergency_contact_2_email_address = Column(String(255))
    emergency_contact_2_first_name = Column(String(255))
    emergency_contact_2_last_name = Column(String(255))
    emergency_contact_2_prefix = Column(String(255))
    emergency_contact_2_relationship = Column(String(255))
    emergency_contact_2_telephone = Column(String(255))
    emergency_contact_2_title = Column(String(255))
    emergency_contact_3_email = Column(String(255))
    emergency_contact_3_email_address = Column(String(255))
    emergency_contact_3_first_name = Column(String(255))
    emergency_contact_3_last_name = Column(String(255))
    emergency_contact_3_relationship = Column(String(255))
    emergency_contact_3_telephone = Column(String(255))
    emergency_contact_3_title = Column(String(255))
    emergency_contact_4_email = Column(String(255))
    emergency_contact_4_email_address = Column(String(255))
    emergency_contact_4_first_name = Column(String(255))
    emergency_contact_4_last_name = Column(String(255))
    emergency_contact_4_relationship = Column(String(255))
    emergency_contact_4_telephone = Column(String(255))
    emergency_contact_4_title = Column(String(255))
    emergency_contact_5_email_address = Column(String(255))
    emergency_contact_5_first_name = Column(String(255))
    emergency_contact_5_last_name = Column(String(255))
    emergency_contact_5_relationship = Column(String(255))
    emergency_contact_5_telephone = Column(String(255))
    emergency_contact_6_email_address = Column(String(255))
    emergency_contact_6_first_name = Column(String(255))
    emergency_contact_6_last_name = Column(String(255))
    emergency_contact_6_relationship = Column(String(255))
    emergency_contact_6_telephone = Column(String(255))
    emergency_contact_7_email_address = Column(String(255))
    emergency_contact_7_first_name = Column(String(255))
    emergency_contact_7_last_name = Column(String(255))
    emergency_contact_7_relationship = Column(String(255))
    emergency_contact_7_telephone = Column(String(255))
    emergency_contact_8_email_address = Column(String(255))
    emergency_contact_8_first_name = Column(String(255))
    emergency_contact_8_last_name = Column(String(255))
    emergency_contact_8_relationship = Column(String(255))
    emergency_contact_8_telephone = Column(String(255))
    emergency_contact_9_email_address = Column(String(255))
    emergency_contact_9_first_name = Column(String(255))
    emergency_contact_9_last_name = Column(String(255))
    emergency_contact_9_relationship = Column(String(255))
    emergency_contact_9_telephone = Column(String(255))
    health_information_1_approved_medications = Column(String(255))
    health_information_1_asthma = Column(String(255))
    health_information_1_asthma_history = Column(String(255))
    health_information_1_blood_type = Column(String(255))
    health_information_1_diabetes = Column(String(255))
    health_information_1_diabetes_history = Column(String(255))
    health_information_1_disorders = Column(String(255))
    health_information_1_frequent_headaches = Column(String(255))
    health_information_1_frequent_headaches_history = Column(String(255))
    health_information_1_health_allergies_description = Column(String(255))
    health_information_1_health_allergies_yes_no = Column(String(255))
    health_information_1_health_medication_description = Column(String(255))
    health_information_1_health_medication_yes_no = Column(String(255))
    health_information_1_health_participation_description = Column(String(255))
    health_information_1_health_participation_file = Column(String(255))
    health_information_1_health_participation_yes_no = Column(String(255))
    health_information_1_health_treatment_description = Column(String(255))
    health_information_1_health_treatment_file = Column(String(255))
    health_information_1_health_treatment_yes_no = Column(String(255))
    health_information_1_hearing_difficulties = Column(String(255))
    health_information_1_hearing_difficulties_history = Column(String(255))
    health_information_1_heart_problems = Column(String(255))
    health_information_1_heart_problems_history = Column(String(255))
    health_information_1_other_health_problems = Column(String(255))
    health_information_1_other_health_problems_history = Column(String(255))
    health_information_1_other_information = Column(String(255))
    health_information_1_psychological_conditions = Column(String(255))
    health_information_1_psychological_conditions_history = Column(String(255))
    health_information_1_seizure_disorder_epilepsy = Column(String(255))
    health_information_1_seizure_history = Column(String(255))
    health_information_1_skin_problems = Column(String(255))
    health_information_1_skin_problems_history = Column(String(255))
    health_information_1_stomach_digestion_problems = Column(String(255))
    health_information_1_stomach_digestion_problems_history = Column(String(255))
    health_information_1_visual_difficulties = Column(String(255))
    health_information_1_visual_difficulties_history = Column(String(255))
    health_information_2_approved_medications = Column(String(255))
    health_information_2_asthma = Column(String(255))
    health_information_2_asthma_history = Column(String(255))
    health_information_2_blood_type = Column(String(255))
    health_information_2_diabetes = Column(String(255))
    health_information_2_diabetes_history = Column(String(255))
    health_information_2_frequent_headaches = Column(String(255))
    health_information_2_frequent_headaches_history = Column(String(255))
    health_information_2_health_allergies_description = Column(String(255))
    health_information_2_health_allergies_yes_no = Column(String(255))
    health_information_2_health_medication_description = Column(String(255))
    health_information_2_health_medication_yes_no = Column(String(255))
    health_information_2_health_participation_description = Column(String(255))
    health_information_2_health_participation_file = Column(String(255))
    health_information_2_health_participation_yes_no = Column(String(255))
    health_information_2_health_treatment_description = Column(String(255))
    health_information_2_health_treatment_file = Column(String(255))
    health_information_2_health_treatment_yes_no = Column(String(255))
    health_information_2_hearing_difficulties = Column(String(255))
    health_information_2_hearing_difficulties_history = Column(String(255))
    health_information_2_heart_problems = Column(String(255))
    health_information_2_heart_problems_history = Column(String(255))
    health_information_2_other_health_problems = Column(String(255))
    health_information_2_other_health_problems_history = Column(String(255))
    health_information_2_other_information = Column(String(255))
    health_information_2_psychological_conditions = Column(String(255))
    health_information_2_psychological_conditions_history = Column(String(255))
    health_information_2_seizure_disorder_epilepsy = Column(String(255))
    health_information_2_seizure_history = Column(String(255))
    health_information_2_skin_problems = Column(String(255))
    health_information_2_skin_problems_history = Column(String(255))
    health_information_2_stomach_digestion_problems = Column(String(255))
    health_information_2_stomach_digestion_problems_history = Column(String(255))
    health_information_2_visual_difficulties = Column(String(255))
    health_information_2_visual_difficulties_history = Column(String(255))
    immunization_record_1_bcg_date = Column(String(255))
    immunization_record_1_bcg_question = Column(String(255))
    immunization_record_1_dtp_dp_date = Column(String(255))
    immunization_record_1_dtp_dp_question = Column(String(255))
    immunization_record_1_hepatitis_a_date = Column(String(255))
    immunization_record_1_hepatitis_a_question = Column(String(255))
    immunization_record_1_hepatitis_b_date = Column(String(255))
    immunization_record_1_hepatitis_b_question = Column(String(255))
    immunization_record_1_hib_date = Column(String(255))
    immunization_record_1_hib_question = Column(String(255))
    immunization_record_1_immunization_file = Column(String(255))
    immunization_record_1_japanese_b_encephalitis_date = Column(String(255))
    immunization_record_1_japanese_b_encephalitis_question = Column(String(255))
    immunization_record_1_mmr_date = Column(String(255))
    immunization_record_1_mmr_question = Column(String(255))
    immunization_record_1_opv_ipv_date = Column(String(255))
    immunization_record_1_opv_ipv_question = Column(String(255))
    immunization_record_1_varicella_chicken_pox_date = Column(String(255))
    immunization_record_1_varicella_chicken_pox_question = Column(String(255))


    @hybrid_property
    def emergency_info(self):
        concat = {}
        for attr in self.__dict__.keys():
            if attr.startswith('emergency_contact') and getattr(self, attr):
                num = re.findall('\d+', attr)
                num = num[0] if num else None
                if not num:
                    continue
                if not num in concat.keys():
                    concat[num] = EmergInfo(num)
                item = concat[num]
                field = re.findall('\d+_(.*)', attr)
                field = field[0] if field else None
                if not field:
                    continue
                field = field.lower()
                setattr(item, field, getattr(self, attr))

        concat_str = ""
        for key in sorted(concat.keys()):
            item = concat[key]
            concat_str += " " + str(item)

        return concat_str

    @hybrid_property
    def health_information(self):
        concat = ""
        for attr in self.__dict__.keys():
            a = attr.lower()
            if a.startswith('health_information'):
                key = re.findall('health_information_\d+_(.*)', a)
                if not key:
                    continue
                key = key[0]
                value = getattr(self, attr)
                if not value:
                    continue
                raw_value = re.sub('[^a-z]', '', value.lower())
                if value and not (raw_value == "no" or raw_value == 'none'):
                    concat += key.replace('_', ' ').replace('description', '').upper().strip() + ": " + value + " "
        return concat

    @hybrid_property
    def immunization_record(self):
        concat = ""
        for attr in self.__dict__.keys():
            a = attr.lower()
            if a.startswith('immunization_record'):
                key = re.findall('immunization_record_\d+_(.*)', a)
                if not key:
                    continue
                key = key[0]
                value = getattr(self, attr)
                if not value:
                    continue
                raw_value = re.sub('[^a-z]', '', value.lower())
                if value and not (raw_value == "no" or raw_value == 'none'):
                    concat += key.replace('_', ' ').replace('description', '').upper().strip() + ": " + value + " "
        return concat

