"""
The file lets me sort out the model for myself
1) Downloads info that is available via API into files
2) Puts it into database

Excuse the mess, it works well enough but isn't exactly clear what's happening
In particular errors aren't handled (FIXME)
"""

import requests
from model import Abstract, Container
import json
import os.path
import re, glob
from db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
from collections import defaultdict
collect_areas = defaultdict(list)

import gns

class APIDownloader(object, lazy=True):
	"""
	Responsible for initial downloads from API
	"""	

	def __init__(self, prefix=None, api_token=None, lazy=True):
		"""
		Sent in optional params can override settings.ini, useful for debugging
		"""
		self.database = Database()
		self.prefix = prefix or gns.config.managebac.prefix
		self.api_token = api_token or gns.config.managebac.api_token

		self.url = gns('https://{prefix}.managebac.com/api/{{}}', prefix=self.prefix)
		# TODO: Make this a setting
		self.sections = ('users', 'classes', 'ib_groups')
		self.section_urls = {'users': 'users/{}', 'classes': 'groups/{}/members', 'ib_groups': 'groups/{}/members'}
		self.container = Container()

		self.path_to_jsons = gns.config.paths.jsons

		if self.path_to_jsons[-1] != '/':
			# ensure path has trailing slash
			self.path_to_jsons += '/'

		if not lazy:
			# Immediately do our thang.
			self.download(overwrite=True)
			self.setup_database()

	def build_json_path(self, *args):
		"""
		Pass it a variable number of parameters to build the path to json
		"""
		return "{}{}".format(self.path_to_jsons, "".join(args))

	def setup_database(self):
		"""
		Reads in file information (made from Go.download) and sets up the database structures
		"""
		for area, key in [('users', 'users'), ('classes', 'classes'), ('ib_groups', 'ib_groups')]:

			with open(self.build_json_path(area, '.json')) as _f:
				this_json = json.load(_f)


			with DBSession() as session:
				for item in this_json[key]:
					_type = item.get('type', None)
					if _type == "Classes":
						print('type is classes')
						_type = "Course"
					if not _type:
						if key == 'ib_groups':
							_type = "IBGroup"
						else:
							_type = 'Course' if item.get('class_type') else None
					if not _type:
						print("Object is causing us trouble: 'item' doesn't have legit 'type'?")
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

		# Downloading concluded, let's popular the database
		# First we need a reference to the tables.
		# Uses sqlalchemy tools to poplate

		Student = self.database.table_string_to_class('Student')
		Teacher = self.database.table_string_to_class('Advisor')
		Parent = self.database.table_string_to_class('Parent')
		Course = self.database.table_string_to_class('Course')
		IBGroup = self.database.table_string_to_class('IBGroup')

		with open(self.build_json_path('/users.json')) as _f:
			this_json = json.load(_f)

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

		with open(self.build_json_path('ib_groups.json')) as _f:
			this_json = json.load(_f)

		for ib_group in this_json['ib_groups']:
			ib_group_id = ib_group.get('id')

			with open(self.build_json_path('groups-{}-members.json'.format(ib_group_id))) as _f2:
				members_json = json.load(_f2)

			for student_item in members_json['members']:
				student_id = student_item.get('student_id')
				if not student_id:
					continue
				with DBSession() as session:
					try:
						student = session.query(Student).filter_by(student_id=student_id).one()
						group = session.query(IBGroup).filter_by(id=ib_group_id).one()
					except NoResultFound:
						continue
					student.ib_groups.append(group)  # adds the ib_group members relation stuff

		with open(self.build_json_path('classes.json')) as _f:
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

		for path in glob.glob(self.build_json_path('groups-*-members.json')):
			with open(path) as _f:
				this_json = json.load(_f)

			with DBSession() as session:
				course_id = re.match(self.build_json_path('groups-(\d+)-members.json'), path).group(1)
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


	def download(self, overwrite=False):
		"""
		Downloads known paths from api and places it onto directories
		"""
		if overwrite:
			if os.path.isdir(self.build_json_path()):
				import shutil
				shutil.rmtree(self.build_json_path())
			else:
				print('overwrite=True passed but path does not exist')

		if not os.path.isdir(self.build_json_path()):
			os.mkdir(self.build_json_path())

		for section in self.sections:
			fileexists = os.path.isfile(self.build_json_path(section, '.json'))

			if not fileexists:
				print('no {} file, downloading'.format(self.build_json_path(section, '.json')))

				r = requests.get(url.format(section), params=dict(
					auth_token=api_token
					))
				try:
					if not r.ok:
						raw_input()
					json_info = r.json()
				except ValueError:
					from IPython import embed; embed()
					continue

			else:
				with open(self.build_json_path(section, '.json')) as _f:
					json_info = json.load(_f)

			if not fileexists:
				with open(self.build_json_path(section, '.json', 'w') as _f:
					json.dump(json_info, _f, indent=4)

			if section in json_info:
				for item in json_info[section]:
					self.container.add(item, section)

		for section in self.sections:
			section_url = self.section_urls.get(section)
			if not section_url:
				# skips ib_groups
				continue

			container_area = getattr(self.container, section)
			for item in container_area:
				if not item:
					continue
				this_url = section_url.format(item.id)
				this_filename = this_url.replace('/', '-')
				fileexists = os.path.isfile(self.build_json_path(this_filename, '.json'))
				if not fileexists:
					r = requests.get(url.format(this_url), params=dict(
						auth_token=api_token
						))
					try:
						json_info = r.json()
					except ValueError:
						print('Trouble with json')
						continue

				else:
					with open(self.build_json_path(this_filename, '.json')) as _f:
						json_info = json.load(_f)

				if not fileexists:
					with open(self.build_json_path(this_filename, '.json'), 'w') as _f:
						json.dump(json_info, _f, indent=4)		


if __name__ == "__main__":

	go = Downloader()

	go.download(overwrite=False)
	go.setup_database()





