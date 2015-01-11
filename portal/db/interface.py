from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
import portal.settings as settings
import gns
import re, json, glob

class DatabaseSetterUpper(object):

	def __init__(self, lazy=True, verbose=False):
		self.database = Database()
		settings.setup_verbosity(self)
		if not lazy:
			self.setup_database()

	def setup_database(self):
		"""
		Reads in file information (made from Go.download) and sets up the database structures
		"""
		settings.get('MANAGEBAC', 'sections', required=True)
		settings.get('DIRECTORIES', 'path_to_jsons', required=True)
		settings.get('MANAGEBAC', 'ib_groups_section_url')

		for gns.section in gns.settings.sections:
			self.default_logger(gns("Setup {section} on database"))

			with open(gns('{settings.path_to_jsons}/{section}.json')) as _f:
				this_json = json.load(_f)

			_map = dict(Classes="Course", Students="Student", Advisors="Advisor", Parents="Parent")

			with DBSession() as session:
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
						setattr(instance, item_key, item[item_key])

					session.add(instance)

		# Uses sqlalchemy tools to poplate

		Student = self.database.table_string_to_class('Student')
		Teacher = self.database.table_string_to_class('Advisor')
		Parent = self.database.table_string_to_class('Parent')
		Course = self.database.table_string_to_class('Course')
		IBGroup = self.database.table_string_to_class('IBGroup')

		with open(gns('{settings.path_to_jsons}/users.json')) as _f:
			this_json = json.load(_f)

		self.default_logger("Setting up student-parent relations on database")
		for user in this_json['users']:
			with DBSession() as session:
				_type = user.get('type')

				if _type == "Students":
					student_id = user.get('student_id')
					if student_id:
						student = session.query(Student).filter_by(student_id=user.get('student_id')).one()
						for parent_id in user.get('parents_ids'):
							parent = session.query(Parent).filter_by(id=parent_id).one()

							student.parents.append(parent)  # adds the parent/child relation stuff automagically

		self.default_logger("Setting up student IB Group membership on database")
		with open(gns('{settings.path_to_jsons}/ib_groups.json')) as _f:
			this_json = json.load(_f)

		for ib_group in this_json['ib_groups']:
			gns.id = ib_group.get('id')
			gns.uri = gns.settings.ib_groups_section_url.replace('/', '-')

			with open(gns(gns('{settings.path_to_jsons}/{uri}.json'))) as _f2:
				members_json = json.load(_f2)

			for student_item in members_json['members']:
				student_id = student_item.get('student_id')
				if not student_id:
					continue
				with DBSession() as session:
					try:
						student = session.query(Student).filter_by(student_id=student_id).one()
						group = session.query(IBGroup).filter_by(id=gns.id).one()
					except NoResultFound:
						continue
					student.ib_groups.append(group)  # adds the ib_group members relation stuff

		self.default_logger("Setting up teacher class assignments on database")
		with open(gns('{settings.path_to_jsons}/classes.json')) as _f:
			this_json = json.load(_f)
		for clss in this_json['classes']:
			for teacher in clss.get('teacher'):
				teacher_id = teacher.get('teacher_id')
				course_id = clss.get('id')

				if teacher_id and course_id:
					with DBSession() as session:
						try:
							teacher = session.query(Teacher).filter_by(id=teacher_id).one()
							course = session.query(Course).filter_by(id=course_id).one()
						except NoResultFound:
							continue
						teacher.classes.append(course)  # adds the teacher assignment stuff

		self.default_logger("Setting up student class enrollments on database")
		for path in glob.glob(gns('{settings.path_to_jsons}/groups-*-members.json')):
			with open(path) as _f:
				this_json = json.load(_f)

			with DBSession() as session:
				course_id = re.match(gns('{settings.path_to_jsons}/groups-(\d+)-members.json'), path).group(1)
				for course in this_json['members']:
					student_id = course.get('student_id')
					if student_id is None:
						continue
					try:
						student = session.query(Student).filter_by(student_id=student_id).one()
						course = session.query(Course).filter_by(id=course_id).one()
					except NoResultFound:
						continue
					student.classes.append(course)  # add the course/students relation stuff

		self.default_logger("Setting up additional accounts manually, those who are admins & teachers")

		with DBSession() as session:
			adam = Teacher(
				id = 10792616,
				first_name= "Adam",
				last_name = "Morris",
				type= "Advisors",
				gender="Male",
				email="adam.morris@igbis.edu.my"
				)


			geoff = Teacher(
				id = 10792598,
				first_name="Geoff",
				last_name ="Derry",
				email="geoffrey.derry@igbis.edu.my",
				type="Advisor"
				)

			matt = Teacher(
				id=10792614,
				first_name="Matthew",
				last_name="Marshall",
				email="Matthew.Marshall@igbis.edu.my",
				type="Advisor"
				)

			phil = Teacher(
				id=10792596,
				first_name="Phil",
				last_name="Clark",
				email="Phil.Clark@igbis.edu.my",
				type="Advisor"
				)

			simon = Teacher(
				id = 10792615,
				first_name="Simon",
				last_name= "Millward",
				email="Simon.Millward@igbis.edu.my",
				type="Advisor"
				)

			lennox = Teacher(
				id = 10754285,
				first_name="Lennox",
				last_name="Meldrum",
				email="lennox.meldrum@igbis.edu.my",
				type="Advisor"
				)

			session.add(adam)
			session.add(geoff)
			session.add(matt)
			session.add(phil)
			session.add(simon)
			session.add(lennox)

		self.default_logger("Done!")