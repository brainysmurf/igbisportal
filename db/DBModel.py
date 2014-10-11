"""
Defines the SQL schema that defines our database.
There are tools out there that will define this automatically, but I don't have access to the database store
So instead I wrote it out by hand

This is based on the API that ManageBac gives, I have found that the API in OpenApply is actually different
for example national_id ≠ password_number

So I guess we'll have to figure that out if we choose to go to production quality
"""

from sqlalchemy import BigInteger, Column, Float, Index, Integer, Numeric, SmallInteger, String, Table, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata
from sqlalchemy.orm import relationship, backref

"""
Klunky, but lets me debug quickly
"""
PREFIX = '1_'
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

class User(object):
	"""
	Fields shared by all users
	TODO: Check this more carefully, bound to need some tweaks
	"""
	#__tablename__ = USERS

	id = Column(BigInteger, primary_key=True)
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

"""
Many to many relationships need an association table, this is it for parent/children links
"""
ParentChildren = Table(
	PARENTCHILDREN, Base.metadata,
	Column('parent_id', BigInteger, ForeignKey(PARENTS+'.id'), primary_key=True),
	Column('student_id', String(255), ForeignKey(STUDENTS+'.student_id'), primary_key=True)
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
	Column('student_id', String(255), ForeignKey(STUDENTS+'.student_id'), primary_key=True)
	)

"""
Many to many relationships need an association table, this is it for IBGroups/members links
TODO: Wait, can a user be a member of only one IB Group?
"""
IBGroupMembership = Table(
	IBGROUPSMEMBERSHIP, Base.metadata,
	Column('ib_group_id', BigInteger, ForeignKey(IBGROUPS+'.id'), primary_key=True),
	Column('student_id', String(255), ForeignKey(STUDENTS+'.student_id'), primary_key=True)
	)


class Student(Base, User):
	"""
	I am a student in ManageBac
	"""
	__tablename__ = STUDENTS

	student_id = Column(String(255), nullable=True, unique=True, server_default=None)
	program = Column(String(255), nullable=True, server_default=None)
	class_year = Column(Integer, nullable=True, server_default=None)
	email = Column(String(255), nullable=True, server_default=None)

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
