"""
Defines the SQL schema that defines our database.
There are tools out there that will define this automatically, but I don't have access to the database store
So instead I wrote it out by hand

This is based on the API that ManageBac gives, I have found that the API in OpenApply is actually different
for example national_id not = password_number

So I guess we'll have to figure that out if we choose to go to production quality
"""

from sqlalchemy import BigInteger, Boolean, Enum, Column, Float, Index, Integer, Numeric, SmallInteger, String, Table, Text, ForeignKey, Date
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.orm import column_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.functions import concat
from sqlalchemy import inspect, func

Base = declarative_base()
metadata = Base.metadata
import datetime
from sqlalchemy.orm import relationship, backref

from collections import defaultdict
import re

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
USERS = "{}users".format(PREFIX)
STUDENTS = "{}students".format(PREFIX)
PARENTS = "{}parents".format(PREFIX)
ADVISORS = "{}teachers".format(PREFIX)
COURSES = "{}courses".format(PREFIX)
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

class User(PortalORM):
    """
    Fields shared by all users
    TODO: Check this more carefully, bound to need some tweaks
    """
    type = Column(String(255))

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

    def __str__(self):
        return (self.first_name or "") + ' ' + (self.last_name or "")

class Users(Base, User):
    """
    The basic user information
    """
    __tablename__ = USERS
    id = Column(BigInteger, primary_key=True)

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

    nickname = Column(String(255))

    parents = relationship('Parent', secondary=ParentChildren, backref='children')
    classes = relationship('Course', secondary=Enrollment, backref='students')
    ib_groups = relationship('IBGroup', secondary=IBGroupMembership, backref='students')

    language = Column(String(255))   # only one with language and not languageX  HUH

    attendance_start_date = Column(String(255))
    birthday = Column(String(255))

    open_apply_student_id = Column(String(255))
    homeroom_advisor = Column(BigInteger, ForeignKey(ADVISORS+'.id'))

    @hybrid_property
    def start_date(self):
        """
        Python date object of when the student starts school
        """
        str_value = self.attendance_start_date
        if not str_value:
            return None
        return datetime.datetime.strptime(str_value, '%Y-%M-%d')

    @hybrid_property
    def parent_name_1(self):
        parents = self.parents
        if len(parents) > 0:
            parent = parents[0]
            return parent.first_name + ' ' + parent.last_name
        return ""

    @hybrid_property
    def parent_name_2(self):
        parents = self.parents
        if len(parents) > 1:
            parent = parents[1]
            return parent.first_name + ' ' + parent.last_name
        return ""

    @hybrid_property
    def parent_email_1(self):
        parents = self.parents
        if len(parents) > 0:
            parent = parents[0]
            return parent.email
        return ""

    @hybrid_property
    def parent_email_2(self):
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
            s += "({}) {} {} {}".format(p+1, parent.name, parent.email, parent.phone_number, parent.mobile_phone_number, parent.street_address, parent.street_address_ii)
        return s

    @hybrid_property
    def program_of_study(self):
        return ", ".join([g.program.upper() for g in self.ib_groups])

    @hybrid_property
    def teacher_emails(self):
        lst = []
        for course in self.classes:
            for teacher in course.teachers:
                lst.append(teacher.email)
        return ", ".join(lst)

    @hybrid_property
    def teacher_names(self):
        lst = []
        for course in self.classes:
            for teacher in course.teachers:
                lst.append(teacher.first_name + ' ' + teacher.last_name)
        return ", ".join(lst)

    @hybrid_property
    def first_nickname_last_studentid(self):
        return self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') + ' ' + self.last_name + ' [' + str(self.student_id) + ']'

    @first_nickname_last_studentid.expression
    def first_nickname_last_studentid(cls):
        return cls.first_name + (' (' + cls.nickname + ')' if cls.nickname and cls.nickname != cls.first_name else '') + ' ' + cls.last_name + ' [' + str(cls.student_id) + ']'

    @hybrid_property
    def first_nickname_last(self):
        return self.first_nickname + ' ' + self.last_name

    @hybrid_property
    def first_nickname(self):
        return self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') 

    @hybrid_property
    def grade_first_nickname_last_studentid(self):
        return str(self.grade or '-10') + ': ' + self.first_name + (' (' + self.nickname + ')' if self.nickname and self.nickname != self.first_name else '') + ' ' + self.last_name + ' [' + str(self.student_id) + ']'

    @hybrid_property
    def grade(self):
        return -10 if self.class_year is None else int(self.class_year) - 1

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
        from portal.db import DBSession, Database
        db = Database()
        from sqlalchemy.orm.exc import NoResultFound
        Teachers = db.table_string_to_class('advisor')

        with DBSession() as session:
            try:
                hr_teacher = session.query(Teachers).filter_by(id=self.homeroom_advisor).one()
            except NoResultFound:
                return "<>"

            return hr_teacher.email

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

    @hybrid_property
    def igbis_username(self):
        return "{}.{}.parent".format(re.sub('[^0-9a-z]', '', self.first_name.replace(' ', '').lower()), re.sub('[^0-9a-z]', '', self.last_name.replace(' ', '').lower()))

    @hybrid_property
    def igbis_email_address(self):
        return self.igbis_username + '@igbis.edu.my'

    @hybrid_property
    def name(self):
        return self.first_name + ' ' + self.last_name

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
    uniq_id = Column(String(255), nullable=True, unique=True, server_default=None)

    # timetables relation defined by Timetable.course 'backref'

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

    Health_Information_1_Health_Allergies_Description = Column(String(255))
    Health_Information_1_Health_Medication_Description = Column(String(255))
    Health_Information_1_Health_Allergies_Yes_No = Column(String(255))
    Health_Information_1_Health_Medication_Yes_No = Column(String(255))
    Health_Information_1_Approved_medications = Column(String(255))
    Health_Information_1_Health_Treatment_Yes_No = Column(String(255))
    Health_Information_1_Health_Treatment_Description = Column(String(255))
    Health_Information_1_Health_Treatment_File = Column(String(255))
    Health_Information_1_Health_Participation_Yes_No = Column(String(255))
    Health_Information_1_Health_Participation_Description = Column(String(255))
    Health_Information_1_Health_Participation_File = Column(String(255))
    Health_Information_1_Frequent_Headaches = Column(String(255))
    Health_Information_1_Frequent_Headaches_History = Column(String(255))
    Health_Information_1_Heart_problems = Column(String(255))
    Health_Information_1_Heart_problems_history = Column(String(255))
    Health_Information_1_Asthma = Column(String(255))
    Health_Information_1_Asthma_history = Column(String(255))
    Health_Information_1_Stomach_digestion_problems = Column(String(255))
    Health_Information_1_Stomach_digestion_problems_history = Column(String(255))
    Health_Information_1_Skin_problems = Column(String(255))
    Health_Information_1_Skin_problems_history = Column(String(255))
    Health_Information_1_Diabetes = Column(String(255))
    Health_Information_1_Diabetes_History = Column(String(255))
    Health_Information_1_Seizure_disorder_epilepsy = Column(String(255))
    Health_Information_1_Seizure_History = Column(String(255))
    Health_Information_1_Psychological_conditions = Column(String(255))
    Health_Information_1_Psychological_conditions_history = Column(String(255))
    Health_Information_1_Hearing_Difficulties = Column(String(255))
    Health_Information_1_Hearing_Difficulties_History = Column(String(255))
    Health_Information_1_Visual_Difficulties = Column(String(255))
    Health_Information_1_Visual_Difficulties_History = Column(String(255))
    Health_Information_1_Other_Health_Problems = Column(String(255))
    Health_Information_1_Other_Health_Problems_History = Column(String(255))
    Health_Information_1_Blood_type = Column(String(255))
    Health_Information_1_Other_Information = Column(String(255))
    Health_Information_2_Health_Allergies_Description = Column(String(255))
    Health_Information_2_Health_Medication_Description = Column(String(255))
    Health_Information_2_Health_Allergies_Yes_No = Column(String(255))
    Health_Information_2_Health_Medication_Yes_No = Column(String(255))
    Health_Information_2_Approved_medications = Column(String(255))
    Health_Information_2_Health_Treatment_Yes_No = Column(String(255))
    Health_Information_2_Health_Treatment_Description = Column(String(255))
    Health_Information_2_Health_Treatment_File = Column(String(255))
    Health_Information_2_Health_Participation_Yes_No = Column(String(255))
    Health_Information_2_Health_Participation_Description = Column(String(255))
    Health_Information_2_Health_Participation_File = Column(String(255))
    Health_Information_2_Frequent_Headaches = Column(String(255))
    Health_Information_2_Frequent_Headaches_History = Column(String(255))
    Health_Information_2_Heart_problems = Column(String(255))
    Health_Information_2_Heart_problems_history = Column(String(255))
    Health_Information_2_Asthma = Column(String(255))
    Health_Information_2_Asthma_history = Column(String(255))
    Health_Information_2_Stomach_digestion_problems = Column(String(255))
    Health_Information_2_Stomach_digestion_problems_history = Column(String(255))
    Health_Information_2_Skin_problems = Column(String(255))
    Health_Information_2_Skin_problems_history = Column(String(255))
    Health_Information_2_Diabetes = Column(String(255))
    Health_Information_2_Diabetes_History = Column(String(255))
    Health_Information_2_Seizure_disorder_epilepsy = Column(String(255))
    Health_Information_2_Seizure_History = Column(String(255))
    Health_Information_2_Psychological_conditions = Column(String(255))
    Health_Information_2_Psychological_conditions_history = Column(String(255))
    Health_Information_2_Hearing_Difficulties = Column(String(255))
    Health_Information_2_Hearing_Difficulties_History = Column(String(255))
    Health_Information_2_Visual_Difficulties = Column(String(255))
    Health_Information_2_Visual_Difficulties_History = Column(String(255))
    Health_Information_2_Other_Health_Problems = Column(String(255))
    Health_Information_2_Other_Health_Problems_History = Column(String(255))
    Health_Information_2_Blood_type = Column(String(255))
    Health_Information_2_Other_Information = Column(String(255))
    Emergency_Contact_1_First_Name = Column(String(255))
    Emergency_Contact_1_Last_Name = Column(String(255))
    Emergency_Contact_1_Telephone = Column(String(255))
    Emergency_Contact_1_Email_Address = Column(String(255))
    Emergency_Contact_1_Relationship = Column(String(255))
    Emergency_Contact_2_First_Name = Column(String(255))
    Emergency_Contact_2_Last_Name = Column(String(255))
    Emergency_Contact_2_Telephone = Column(String(255))
    Emergency_Contact_2_Email_Address = Column(String(255))
    Emergency_Contact_2_Relationship = Column(String(255))
    Emergency_Contact_3_First_Name = Column(String(255))
    Emergency_Contact_3_Last_Name = Column(String(255))
    Emergency_Contact_3_Telephone = Column(String(255))
    Emergency_Contact_3_Email_Address = Column(String(255))
    Emergency_Contact_3_Relationship = Column(String(255))
    Emergency_Contact_4_First_Name = Column(String(255))
    Emergency_Contact_4_Last_Name = Column(String(255))
    Emergency_Contact_4_Telephone = Column(String(255))
    Emergency_Contact_4_Email_Address = Column(String(255))
    Emergency_Contact_4_Relationship = Column(String(255))
    Emergency_Contact_5_First_Name = Column(String(255))
    Emergency_Contact_5_Last_Name = Column(String(255))
    Emergency_Contact_5_Telephone = Column(String(255))
    Emergency_Contact_5_Email_Address = Column(String(255))
    Emergency_Contact_5_Relationship = Column(String(255))
    Emergency_Contact_6_First_Name = Column(String(255))
    Emergency_Contact_6_Last_Name = Column(String(255))
    Emergency_Contact_6_Telephone = Column(String(255))
    Emergency_Contact_6_Email_Address = Column(String(255))
    Emergency_Contact_6_Relationship = Column(String(255))
    Emergency_Contact_7_First_Name = Column(String(255))
    Emergency_Contact_7_Last_Name = Column(String(255))
    Emergency_Contact_7_Telephone = Column(String(255))
    Emergency_Contact_7_Email_Address = Column(String(255))
    Emergency_Contact_7_Relationship = Column(String(255))
    Emergency_Contact_8_First_Name = Column(String(255))
    Emergency_Contact_8_Last_Name = Column(String(255))
    Emergency_Contact_8_Telephone = Column(String(255))
    Emergency_Contact_8_Email_Address = Column(String(255))
    Emergency_Contact_8_Relationship = Column(String(255))
    Emergency_Contact_9_First_Name = Column(String(255))
    Emergency_Contact_9_Last_Name = Column(String(255))
    Emergency_Contact_9_Telephone = Column(String(255))
    Emergency_Contact_9_Email_Address = Column(String(255))
    Emergency_Contact_9_Relationship = Column(String(255))
    Emergency_Contact_10_First_Name = Column(String(255))
    Emergency_Contact_10_Last_Name = Column(String(255))
    Emergency_Contact_10_Telephone = Column(String(255))
    Emergency_Contact_10_Email_Address = Column(String(255))
    Emergency_Contact_10_Relationship = Column(String(255))
    Emergency_Contact_11_First_Name = Column(String(255))
    Emergency_Contact_11_Last_Name = Column(String(255))
    Emergency_Contact_11_Telephone = Column(String(255))
    Emergency_Contact_11_Email_Address = Column(String(255))
    Emergency_Contact_11_Relationship = Column(String(255))
    Emergency_Contact_12_First_Name = Column(String(255))
    Emergency_Contact_12_Last_Name = Column(String(255))
    Emergency_Contact_12_Telephone = Column(String(255))
    Emergency_Contact_12_Email_Address = Column(String(255))
    Emergency_Contact_12_Relationship = Column(String(255))

    @hybrid_property
    def emergency_info(self):
        concat = {}
        for attr in self.__dict__.keys():
            if attr.startswith('Emergency_Contact') and getattr(self, attr):
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

