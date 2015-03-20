"""
Defines the SQL schema that defines our database.
There are tools out there that will define this automatically, but I don't have access to the database store
So instead I wrote it out by hand

This is based on the API that ManageBac gives, I have found that the API in OpenApply is actually different
for example national_id not = password_number

So I guess we'll have to figure that out if we choose to go to production quality
"""

from sqlalchemy import BigInteger, Boolean, Enum, Column, Float, Index, Integer, Numeric, SmallInteger, String, Table, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata
from sqlalchemy.orm import relationship, backref

"""
Klunky, but lets me debug quickly
"""
PREFIX = 'new_'
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

class User(object):
	"""
	Fields shared by all users
	TODO: Check this more carefully, bound to need some tweaks
	"""
	#__tablename__ = USERS

	type = Column(String(255), nullable=True, server_default=None)

	first_name = Column(String(255), nullable=True, server_default=None)
	last_name = Column(String(255), nullable=True, server_default=None)
	gender = Column(String(255), nullable=True, server_default=None)

	national_id = Column(String(255), nullable=True, server_default=None)   # This is the same as passport ID??  Fix

	nationality1 = Column(String(255), nullable=True, server_default=None)
	nationality2 = Column(String(255), nullable=True, server_default=None)
	nationality3 = Column(String(255), nullable=True, server_default=None)
	nationality4 = Column(String(255), nullable=True, server_default=None)
	language1 = Column(String(255), nullable=True, server_default=None)
	language2 = Column(String(255), nullable=True, server_default=None)
	language3 = Column(String(255), nullable=True, server_default=None)
	language4 = Column(String(255), nullable=True, server_default=None)

	phone_number = Column(String(255), nullable=True, server_default=None)
	mobile_phone_number = Column(String(255), nullable=True, server_default=None)

	street_address = Column(String(255), nullable=True, server_default=None)
	street_address_ii = Column(String(255), nullable=True, server_default=None)
	city = Column(String(255), nullable=True, server_default=None)
	state = Column(String(255), nullable=True, server_default=None)
	zipcode = Column(String(255), nullable=True, server_default=None)

	g_plus_unique_id = Column(String(255), nullable=True, server_default=None)

	def __str__(self):
		return self.first_name + ' ' + self.last_name

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

	student_id = Column(String(255), nullable=True, server_default=None)
	program = Column(String(255), nullable=True, server_default=None)
	class_year = Column(Integer, nullable=True, server_default=None)
	email = Column(String(255), nullable=True, server_default=None)
	nickname = Column(String(255), nullable=True, server_default=None)

	parents = relationship('Parent', secondary=ParentChildren, backref='children')
	classes = relationship('Course', secondary=Enrollment, backref='students')
	ib_groups = relationship('IBGroup', secondary=IBGroupMembership, backref='students')

	language = Column(String(255), nullable=True, server_default=None)   # only one with language and not languageX  HUH

	attendance_start_date = Column(String(255), nullable=True, server_default=None)
	birthday = Column(String(255), nullable=True, server_default=None)

	open_apply_student_id = Column(String(255), nullable=True, server_default=None)


class Parent(Base, User):
	"""
	I am a parent in ManageBac

	TODO: Create some glue code that makes a 'work_info' Many-to-one relation
	"""
	__tablename__ = PARENTS

	id = Column(BigInteger, primary_key=True)

	nickname = Column(String(255), nullable=True, server_default=None)
	salutation = Column(String(255), nullable=True, server_default=None)

	employer = Column(String(255), nullable=True, server_default=None)
	title = Column(String(255), nullable=True, server_default=None)

	openapply_parent_id = Column(String(255), nullable=True, server_default=None)
	openapply_student_id = Column(String(255), nullable=True, server_default=None)

	# children relation made by Student.parents 'backref'

	# FIXME: This is crazy, why define the work info for each parent??
	work_street_address = Column(String(255), nullable=True, server_default=None)
	work_street_address_ii = Column(String(255), nullable=True, server_default=None)
	work_city = Column(String(255), nullable=True, server_default=None)
	work_state = Column(String(255), nullable=True, server_default=None)
	work_zipcode = Column(String(255), nullable=True, server_default=None)

class Advisor(Base, User):
	"""
	I am a teacher in ManageBac, obviously we call them advisors for legacy reasons
	"""

	__tablename__ = ADVISORS

	id = Column(BigInteger, primary_key=True)

	first_name = Column(String(255), nullable=True, server_default=None)
	last_name = Column(String(255), nullable=True, server_default=None)
	national_id = Column(String(255), nullable=True, server_default=None)
	classes = relationship('Course', secondary=Assignment, backref='teachers')

	email = Column(String(255), nullable=True, server_default=None)

class Course(Base):
	"""
	I am a course/class in ManageBac (class is a reserved word in Python)
	Includes timetable / period information
	"""
	__tablename__ = COURSES

	id = Column(BigInteger, primary_key=True)
	type = Column(String(255), nullable=True, server_default=None)
	name = Column(String(255), nullable=True, server_default=None)
	grade = Column(String(255), nullable=True, server_default=None)
	uniq_id = Column(String(255), nullable=True, unique=True, server_default=None)

	# timetables relation defined by Timetable.course 'backref'

class Timetable(Base):
	"""
	Composite primary key consisting of course_id (ForeignKey) and day and period info
	"""
	__tablename__ = TIMETABLES

	course_id = Column(BigInteger, ForeignKey(COURSES+'.id'), primary_key=True)
	day = Column(Integer, nullable=True, server_default=None, primary_key=True)
	period = Column(Integer, nullable=True, server_default=None, primary_key=True)

	course = relationship('Course', backref='timetables')

	def __str__(self):
		return str(self.day) + ': ' + str(self.period)


class IBGroup(Base):
	"""
	I am an IBGroup in ManageBac
	"""
	__tablename__ = IBGROUPS

	id = Column(BigInteger, primary_key=True)

	grade = Column(String(255), nullable=True, server_default=None)
	program = Column(String(255), nullable=True, server_default=None)
	name = Column(String(255), nullable=True, server_default=None)
	unique_id = Column(String(255), nullable=True, server_default=None)

class SecondaryHomeroomTeachers(Base):
	__tablename__ = SECHRTEACHERS

	id = Column(BigInteger, primary_key=True, nullable=True, server_default=None)

	student_id = Column(BigInteger, ForeignKey(STUDENTS+'.id'), nullable=True, server_default=None)
	teacher_id = Column(BigInteger, ForeignKey(ADVISORS+'.id'), nullable=True, server_default=None)

class AuditLog(Base):
	__tablename__ = AUDITLOGS
	id = Column(BigInteger, primary_key=True)
	date = Column(String(255), nullable=True, server_default=None)
	target = Column(String(255), nullable=True, server_default=None)
	administrator = Column(String(255), nullable=True, server_default=None)
	applicant = Column(String(255), nullable=True, server_default=None)
	action = Column(String(1000), nullable=True, server_default=None)

class Terms(Base):
	"""
	TODO: What about academic start date?
	"""
	__tablename__ = TERMS

	id = Column(BigInteger, primary_key=True)
	name = Column(String(255), nullable=True, server_default=None)
	start_date = Column(String(255), nullable=True, 	server_default=None)
	end_date = Column(String(255), nullable=True, server_default=None)
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

	text = Column(String(1000), nullable=True, server_default=None)

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

	homeroom_comment = Column(String(2000), nullable=True, server_default=None)

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

	name = Column(String(500), nullable=True, server_default=None)
	comment = Column(String(2000), nullable=True, server_default=None)
	
	teachers = relationship('Advisor', secondary=primary_report_section_teacher_association)
	strands = relationship('PrimaryReportStrand')
	learning_outcomes = relationship('PrimaryReportLo')


class PrimaryReportStrand(Base):
	__tablename__ = PRIMARYREPORTSTRAND
	id = Column(BigInteger, primary_key=True)
	primary_report_section_id = Column(ForeignKey(PRIMARYREPORTSECTION + '.id'))
	which = Column(Integer, nullable=True, server_default=None)

	label = Column(String(1000), nullable=True, server_default=None)
	label_titled = Column(String(1000), nullable=True, server_default=None)
	selection = Column(String(4), nullable=True, server_default=None)
	#selection = Column(Enum('', 'W', 'S', 'I', 'E', name = 'selection'))

class PrimaryReportLo(Base):
	__tablename__ = PRIMARYREPORTLO
	id = Column(BigInteger, primary_key=True)
	primary_report_section_id = Column(ForeignKey(PRIMARYREPORTSECTION + '.id'))
	which = Column(Integer, nullable=True, server_default=None)

	heading = Column(String(1000), nullable=True, server_default=None)	
	label = Column(String(1000), nullable=True, server_default=None)
	label_titled = Column(String(1000), nullable=True, server_default=None)
	selection = Column(String(4), nullable=True, server_default=None)
	#selection = Column(Enum('', 'O', 'G', 'N', name = 'selection'))

class PrimaryTeacherAssignments(Base):
	__tablename__ = PYPTEACHERASSIGNMENTS
	id = Column(BigInteger, primary_key=True)
	teacher_id = Column(ForeignKey(ADVISORS + '.id'))
	subject_id = Column(BigInteger, nullable=True, server_default=None)
	class_id = Column(ForeignKey(COURSES + '.id'))

class PrimaryStudentAbsences(Base):
	__tablename__ = PYPSTUDENTABSENCES
	id = Column(BigInteger, primary_key=True)
	student_id = Column(ForeignKey(STUDENTS + '.id'))
	term_id = Column(ForeignKey(TERMS + '.id'))
	absences = Column(Integer, nullable=True, server_default=None)
	total_days = Column(Integer, nullable=True, server_default=None)

class GoogleSignIn(Base):
	__tablename__ = "GoogleSignIn"   # NOT based on the prefix...

	id = Column(BigInteger, primary_key=True)
	unique_id = Column(String(1000), nullable=True, server_default=None)
	auth_code = Column(String(255), nullable=True, server_default=None)
	access_token = Column(String(255), nullable=True, server_default=None)
	refresh_token = Column(String(255), nullable=True, server_default=None)

class UserSettings(Base):
	__tablename__ = SETTINGS

	id = Column(BigInteger, primary_key=True)
	unique_id = Column(String(255), nullable=True, server_default=None)
	icon_size = Column(String(2), nullable=True, server_default=None)

