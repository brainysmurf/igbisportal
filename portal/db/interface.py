from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import gns
import re, json, glob

from portal.db.UpdaterHelper import updater_helper

db = Database()
Student = db.table_string_to_class('Student')
Teacher = db.table_string_to_class('Advisor')
Parent = db.table_string_to_class('Parent')
Course = db.table_string_to_class('Course')
IBGroup = db.table_string_to_class('IBGroup')

class DatabaseSetterUpper(object):

	def __init__(self, lazy=True, verbose=False):
		self.database = Database()
		#gns.setup_verbosity(self)
		if not lazy:
			self.setup_database()

	def setup_database(self):
		"""
		Reads in file information (made from Go.download) and sets up the database structures
		"""

		#self.default_logger("Setting up additional accounts manually, those who are admins & teachers")

		admins = []
		admins.append(Teacher(
			id = 10792616,
			first_name= "Adam",
			last_name = "Morris",
			type= "Advisors",
			gender="Male",
			email="adam.morris@igbis.edu.my"
			))

		admins.append(Teacher(
			id = 10792598,
			first_name="Geoff",
			last_name ="Derry",
			email="geoffrey.derry@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id=10792614,
			first_name="Matthew",
			last_name="Marshall",
			email="Matthew.Marshall@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id=10792596,
			first_name="Phil",
			last_name="Clark",
			email="Phil.Clark@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10792615,
			first_name="Simon",
			last_name= "Millward",
			email="Simon.Millward@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10754285,
			first_name="Lennox",
			last_name="Meldrum",
			email="lennox.meldrum@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10792603,
			first_name="Peter",
			last_name="Fowles",
			email="peter.fowles@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10792604,
			first_name="Gail",
			last_name="Hall",
			email="gail.hall@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 13546,
			first_name="Super",
			last_name="Admin",
			email="superadmin@managebac.com",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10958256,
			first_name="Usha",
			last_name ="Ranikrishnan",
			email="usha.ranikrishnan",
			type="Advisor"
			))

		with updater_helper() as u:

			for admin in admins:
				u.update_or_add(admin)

			for gns.section in gns.config.managebac.sections.split(','):
				#self.default_logger(gns("Setup {section} on database"))

				with open(gns('{config.paths.jsons}/{section}.json')) as _f:
					this_json = json.load(_f)

				_map = dict(Classes="Course", Students="Student", Advisors="Advisor", Parents="Parent")

				for item in this_json[gns.section]:
					_type = item.get('type', None)
					_type = _map.get(_type, _type)
					if not _type:
						if gns.section == 'ib_groups':
							_type = "IB_Group"
						else:
							_type = 'Course' if item.get('class_type') else None
					if not _type:
						print("Object is causing us trouble can't go on without resolving: 'item' doesn't have legit 'type'?")
						from IPython import embed
						embed()
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
							if item[item_key] is None:
								continue  # happens when None is put on there
							else:
								# TODO: Figure this out
								# print?
								# print('here')
								# from IPython import embed
								# embed()
								# exit()
								pass

					# Filter out things
					# Don't go ahead unless a studentid has been given
					# TODO: Shouldn't this really be enforced in the model?
					# 		Maybe check for constaints? 
					if _type == "Student":
						if hasattr(item, 'student_id') and not item['student_id'] is None:
							# TODO: Inform someone?
							print('Student without student_id: {}'.format(item))
							continue

					u.update_or_add(instance)

			with u.collection(Student, Parent, 'parents', left_column='student_id') as stu_par:

				with open(gns('{config.paths.jsons}/users.json')) as _f:
					this_json = json.load(_f)

				#self.default_logger("Setting up student-parent relations on database")
				for user in this_json['users']:
					_type = user.get('type')
					if _type == "Students":
						student_id = user.get('student_id')
						if student_id:
							for parent_id in user.get('parents_ids'):
								stu_par.append(student_id, parent_id)

			with u.collection(Student, IBGroup, 'ib_groups', left_column='student_id') as stu_ibgroup:
				#self.default_logger("Setting up student IB Group membership on database")
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
				#self.default_logger("Setting up teacher class assignments on database")
				with open(gns('{config.paths.jsons}/classes.json')) as _f:
					this_json = json.load(_f)
				for clss in this_json['classes']:
					for teacher in clss.get('teacher'):
						teacher_id = teacher.get('teacher_id')
						course_id = clss.get('id')

						if teacher_id and course_id:
							teacher_course.append(teacher_id, course_id)

			with u.collection(Student, Course, 'classes', left_column='student_id') as stu_course:

				#self.default_logger("Setting up student class enrollments on database")
				for path in glob.glob(gns('{config.paths.jsons}/groups-*-members.json')):
					with open(path) as _f:
						this_json = json.load(_f)

					with DBSession() as session:
						course_id = re.match(gns('{config.paths.jsons}/groups-(\d+)-members.json'), path).group(1)
						for course in this_json['members']:
							student_id = course.get('student_id')
							if student_id is None:
								continue
							try:
								stu_course.append(student_id, course_id)
							except NoResultFound:
								pass
								#print('course_id {} or student_id {} not found'.format(course_id, student_id))

			#self.default_logger("Done!")

if __name__ == "__main__":

	go  = DatabaseSetterUpper(lazy=False)
