"""

FIXME: Do not print to stdout	
"""

from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from portal.exceptions import DoesNotExist
from sqlalchemy.exc import IntegrityError
import gns
import re, json, glob

from portal.db.UpdaterHelper import updater_helper

import hashlib # so we can store unique IDs for busadmins

import click


class DatabaseSetterUpper(object):
	"""
	Reads in json files and executes SQL statements on the database to reflect that information
	"""

	def __init__(self, lazy=True):
		self.db = Database()
		if not lazy:
			self.setup_database()

	def default_logger(self, s):
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
						db_student = session.query(self.db.table.Student).filter(self.db.table.Student.student_id==student_student_id).one()
					except NoResultFound:
						try:
							db_student = session.query(self.db.table.Student).filter(self.db.table.Student.email==student_email).one()
						except NoResultFound:
							db_student = None
					except MultipleResultsFound:
						click.echo("More than one account with the same student id of {}".format(student_student_id))
						continue

					# FIXME: Why is db_student.status always None here?
					if db_student and db_student.status != student.get('status'):
						click.echo(u'\t Changed status of {} from {} to {}'.format(db_student, db_student.status, student.get('status')))
						db_student.status = student.get('status')
						session.commit()
					else:
						# Fails silently, expected behavour for a many (no student_id, email doesn't match anymore...)
						pass

	def setup_database(self, fake=False):
		"""
		Reads in file information (made from Go.download) and sets up the database structures
		"""
		if fake:
			from faker import Faker
			fake = Faker()

		gns.tutorial(self.__doc__, banner=True)
		busadmins = []

		# horrible hack-ish
		# open up the file that isn't in the rep, that outputs the group info 
		# for all.team, and then add those that aren't 
		gns.tutorial("Reading in business and administration from google output for all team.  "
			"Please ensure that there is cronjob in place at location {} "
			"to ensure this works properly.".format(gns.config.paths.allteam_file))
		with open(gns.config.paths.allteam_file) as _f:
			for line in _f.readlines():
				if line.startswith(' member:'):
					gns.tutorial("In file, found: {}".format(line), banner=False)
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
					else:
						first = 'Account'
						last = handle.title()

					if fake:
						f_name = "This should not work"
						while len(f_name.split(" ")) != 2:
							f_name = fake.name()
						first, last = f_name.split(" ")

					# This gets a usable unique ID integer to use for IDs
					# very unlikely to produce collisions
					id_ = int(hashlib.md5(handle.encode('utf-8')).hexdigest()[:12], 16)
					gns.tutorial("Generated unique ID to use for id_: {}".format(id_), banner=False)
					busadmins.append(self.db.table.BusAdmin(id=id_, first_name=first, last_name=last, type="BusAdmin", email=user_email))

		with updater_helper() as u:

			for busadmin in busadmins:
				gns.tutorial("Adding admin {} to database".format(busadmin))
				u.update_or_add(busadmin)

			# Section refers to users, groups, etc

			for gns.section in gns.config.managebac.sections.split(','):
				path = gns('{config.paths.jsons}/{section}.json')
				with open(path.replace('_', '-')) as _f:
					this_json = json.load(_f)
				gns.tutorial("Importing {} from file located at {}".format(gns.section, path), edit=(str(this_json), '.json'))
				_map = dict(classes="Course", students="Student", teachers="Advisor", parents="Parent", ib_groups="IBGroup")
				_type = _map.get(gns.section)

				items = this_json[gns.section]
				for item in items:
					if fake and _type in ["Student", "Advisor", "Parent"]:
						f_name = "This should not work"
						while len(f_name.split(" ")) != 2:
							f_name = fake.name()
						item['first_name'], item['last_name'] = f_name.split(" ")
						if item['email'] != 'adam.morris@igbis.edu.my':
							# exclude the admin so I can still log into the portal
							item['email'] = (item['first_name'] + '_' + item['last_name'] + '@example.com').lower()
						if _type == "Student":
							item['nickname'] = item['first_name']

					# Convert any empty string values to None
					item = {k: v if not v == "" else None for k,v in item.items()}
					table_class = self.db.table_string_to_class(_type)
					instance = table_class()
					for item_key in item:
						value = item[item_key]
						if gns.section == "classes" and item_key == 'teachers':
							continue  # don't need to do this as this happens below...
						setattr(instance, item_key, value)
					# Don't go ahead unless a studentid has been given
					if _type == "Student":
						if hasattr(item, 'student_id') and not item['student_id'] is None:
							click.echo(click.style("Warning, student_id not present for {}".format(item)))
							continue
					u.update_or_add(instance)

		with updater_helper() as u:

			with u.collection(self.db.table.Student, self.db.table.Parent, 'parents', left_column='id') as stu_par:

				with open(gns('{config.paths.jsons}/students.json')) as _f:
					this_json = json.load(_f)

				gns.tutorial("Associating students with respective parents")
				for student in this_json['students']:
					student_id = student.get('id')
					if student_id:
						for parent_id in student.get('parent_ids'):
							# This will decide on that end whether or not to emit the sql or not
							try:
								stu_par.append(student_id, parent_id)
							except NoResultFound:
								print("Could not associate {} with {} what the heck?".format(student_id, parent_id))
					else:
						pass # Expected: There are loads of students without any student_id (either none or blank) that are in there for testing, etc

			with u.collection(self.db.table.Student, self.db.table.IBGroup, 'ib_groups', left_column='id') as stu_ibgroup:
				gns.tutorial("Associating students with IB Groups")
				with open(gns('{config.paths.jsons}/ib-groups.json')) as _f:
					this_json = json.load(_f)

				for ib_group in this_json['ib_groups']:
					gns.group_id = ib_group.get('id')
					gns.id = gns.group_id
					gns.uri = gns.config.managebac.ib_groups_section_url.replace('/', '-')

					# Two gns calls because uri has {id} in it
					with open(gns(gns('{config.paths.jsons}/{uri}.json')).replace("_", '-')) as _f2:
						members_json = json.load(_f2)
					for gns.student_id in members_json['student_ids']:
						try:
							stu_ibgroup.append(gns.student_id, gns.group_id)
						except DoesNotExist:
							print("No student going by ID {}".format(gns.student_id))

			with u.collection(self.db.table.Teacher, self.db.table.Course, 'classes') as teacher_course:
				gns.tutorial("Associating teachers with their enrolled classes")
				with open(gns('{config.paths.jsons}/classes.json')) as _f:
					this_json = json.load(_f)
				for clss in this_json['classes']:
					for teacher in [t for t in clss.get('teachers')]:
						teacher_id = teacher.get('teacher_id')
						teacher_course.append(teacher_id, clss['id'])

			with u.collection(self.db.table.Student, self.db.table.Course, 'classes', left_column='id') as stu_course:

				gns.tutorial("Associating students with enrolled classes")
				for path in glob.glob(gns('{config.paths.jsons}/classes-*-students.json')):
					with open(path) as _f:
						this_json = json.load(_f)

					with DBSession() as session:
						course_id = int(re.match(gns('{config.paths.jsons}/classes-(\d+)-students.json'), path).group(1))
						for student_id in this_json['student_ids']:
							# DEBUGGING
							stu_course.append(student_id, course_id)

		# Now let's look at open_apply and update status, but only if the student is already in there.
		# We won't use the manager because this is more of a piece-meal thing

		self.update_status()



if __name__ == "__main__":

	go  = DatabaseSetterUpper(lazy=True)
	go.update_status()
