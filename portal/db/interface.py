from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError
import gns
import re, json, glob

from portal.db.UpdaterHelper import updater_helper

db = Database()
Student = db.table_string_to_class('Student')
Teacher = db.table_string_to_class('Advisor')
BusAdmin = db.table_string_to_class('BusAdmin')
Parent = db.table_string_to_class('Parent')
Course = db.table_string_to_class('Course')
IBGroup = db.table_string_to_class('IBGroup')

import hashlib # so we can store unique IDs for busadmins

import click

class DatabaseSetterUpper(object):

	def __init__(self, lazy=True, verbose=False):
		self.database = Database()
		self.verbose = verbose
		#gns.setup_verbosity(self)
		if not lazy:
			self.setup_database()

	def default_logger(self, s):
		if self.verbose:
			click.echo(s)

	def update_status(self):
		"""
		Special routine for updating status
		Tricky because we cannot assume that student_id will be entered
		Decided to update the status even if there is no student_id provided (which potentially could happen)
		It looks at the student email instead
		"""
		with open(gns('{config.paths.jsons}/open_apply_users.json')) as _f:
			this_json = json.load(_f)

			for student in this_json.get('students'):

				student_student_id = student.get('custom_id')  # open applys stores student_id as custom_id
				student_email = student.get('email')

				with DBSession() as session:

					try:
						if student_student_id is None:
							# short-circuit to checking by email addy
							raise NoResultFound
						db_student = session.query(Student).filter(Student.student_id==student_student_id).one()
					except NoResultFound:
						try:
							db_student = session.query(Student).filter(Student.email==student_email).one()
						except NoResultFound:
							db_student = None

					# FIXME: Why is db_student.status always None here?
					if db_student and db_student.status != student.get('status'):
						click.echo(u'\t Changed status of {} from {} to {}'.format(db_student, db_student.status, student.get('status')))
						db_student.status = student.get('status')
						session.commit()
					else:
						# Fails silently, expected behavour for a many (no student_id, email doesn't match anymore...)
						pass

	def setup_database(self):
		"""
		Reads in file information (made from Go.download) and sets up the database structures
		"""

		busadmins = []

		# horrible hack-ish
		# open up the file that isn't in the rep, that outputs the group info 
		# for all.team, and then add those that aren't 
		with open(gns.config.paths.allteam_file) as _f:
			for line in _f.readlines():
				if line.startswith(' member:'):
					_, pre, user_email, post = line.strip("\n").split(" ")
					handle, _ = user_email.split("@")
					if "." in handle:
						try:
							# most have a dot to seperate first and last names
							first, last = handle.split(".")
						except ValueError:
							# have to do something, so just assume first is before the first dot
							# and last is everything after that
							first = handle.split(".")[0].title()
							last = "".join(handle.split(".")[1:]).title()

						# This gets a usable unique ID integer to use for IDs
						# very unlikely to produce collisions
						id_ = int(hashlib.md5(handle).hexdigest()[:12], 16)
						busadmins.append(BusAdmin(id=id_, first_name=first, last_name=last, type="BusAdmin", email=user_email))

		with updater_helper() as u:

			for busadmin in busadmins:
				u.update_or_add(busadmin)

			# Section refers to users, groups, etc

			for gns.section in gns.config.managebac.sections.split(','):
				self.default_logger(gns("Setup {section} on database"))

				with open(gns('{config.paths.jsons}/{section}.json')) as _f:
					this_json = json.load(_f)

				_map = dict(Classes="Course", Students="Student", Advisors="Advisor", Parents="Parent")
				_map['Account Admins'] = "Advisor"   # count account admins as an advisor
				if gns.section == "users":
					# We need to process the advisors first, otherwise potentially we'll get foreign key constraint errors
					# If we process student before advisor has been created
					items = sorted(this_json[gns.section], key=lambda x: x.get('type'))
				else:
					items = this_json[gns.section]

				for item in items:
					_type = item.get('type', None)
					_type = _map.get(_type, _type)
					if not _type:
						if gns.section == 'ib_groups':
							_type = "IB_Group"
						else:
							_type = 'Course' if item.get('class_type') else None
					if not _type:
						print("Object is causing us trouble can't go on without resolving: 'item' doesn't have legit 'type'?")
						exit()

					# Convert any empty string values to None
					item = {k: v if not v == "" else None for k,v in item.items()}
					table_class = self.database.table_string_to_class(_type)
					instance = table_class()
					for item_key in item:
						try:
							# Set up the instance to have the expected values
							setattr(instance, item_key, item[item_key])

						except AttributeError:
							#TODO: Make this part of the logger
							click.echo(click.style("Warning, no attribute {} for {} detected".format(item_key, item), fg='red'))
							if item[item_key] is None:
								pass # doesn't seem to be happening								
							else:
								pass  # doesn't seem to be happening

					# Don't go ahead unless a studentid has been given
					if _type == "Student":
						if hasattr(item, 'student_id') and not item['student_id'] is None:
							click.echo(click.style("Warning, student_id not present for {}".format(item)))
							continue

					u.update_or_add(instance)

			with u.collection(Student, Parent, 'parents', left_column='student_id') as stu_par:

				with open(gns('{config.paths.jsons}/users.json')) as _f:
					this_json = json.load(_f)

				self.default_logger("Setting up student-parent relations on database")
				for user in this_json['users']:
					_type = user.get('type')
					if _type == "Students":
						student_id = user.get('student_id')	
						for parent_id in user.get('parents_ids'):
							stu_par.append(student_id, parent_id)

			with u.collection(Student, IBGroup, 'ib_groups', left_column='student_id') as stu_ibgroup:
				self.default_logger("Setting up student IB Group membership on database")
				with open(gns('{config.paths.jsons}/ib_groups.json')) as _f:
					this_json = json.load(_f)

				for ib_group in this_json['ib_groups']:
					gns.group_id = ib_group.get('id')
					gns.id = gns.group_id
					gns.uri = gns.config.managebac.ib_groups_section_url.replace('/', '-')

					# Two gns calls because uri has {id} in it
					with open(gns(gns('{config.paths.jsons}/{uri}.json'))) as _f2:
						members_json = json.load(_f2)

					for student_item in members_json['members']:
						gns.student_id = student_item.get('student_id')
						if not gns.student_id:
							continue
						stu_ibgroup.append(gns.student_id, gns.group_id)						

			with u.collection(Teacher, Course, 'classes') as teacher_course:
				self.default_logger("Setting up teacher class assignments on database")
				with open(gns('{config.paths.jsons}/classes.json')) as _f:
					this_json = json.load(_f)
				for clss in this_json['classes']:
					for teacher in clss.get('teacher'):
						teacher_id = teacher.get('teacher_id')
						course_id = clss.get('id')

						if teacher_id and course_id:
							teacher_course.append(teacher_id, course_id)

			with u.collection(Student, Course, 'classes', left_column='student_id') as stu_course:

				self.default_logger("Setting up student class enrollments on database")
				for path in glob.glob(gns('{config.paths.jsons}/groups-*-members.json')):
					with open(path) as _f:
						this_json = json.load(_f)

					with DBSession() as session:
						course_id = re.match(gns('{config.paths.jsons}/groups-(\d+)-members.json'), path).group(1)
						for course in this_json['members']:
							student_id = course.get('student_id')
							successful = False
							try:
								student = session.query(Student).filter(Student.student_id==student_id).one()
								successful = True
							except NoResultFound:
								self.default_logger("Student {} not found".format(student_id))
							except MultipleResultsFound:
								if student_id is None:
									print("student_id is None!")
								else:
									print("Found this student twice! {}".format(student_id))
							if successful:							
								try:
									stu_course.append(str(student.id), course_id)
								except NoResultFound:
									self.default_logger('course_id {} or student_id {} not found'.format(course_id, student_id))

		# Now let's look at open_apply and update status, but only if the student is already in there.
		# We won't use the manager because this is more of a piece-meal thing

		self.update_status()



if __name__ == "__main__":

	go  = DatabaseSetterUpper(lazy=True)
	go.update_status()
