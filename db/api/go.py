"""
The file lets me sort out the model for myself
1) Downloads info that is available via API into files
2) Puts it into database

Excuse the mess, it works well enough but isn't exactly clear what's happening
In particular errors aren't handled (FIXME)
"""

import requests
import redis
from model import Abstract, Container
import json
import os.path
import re, glob
from db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound

database = DataBase()

PREFIX = 'igbis2014'
url = 'https://igbis.managebac.com/api/{}'
sections = ('users', 'classes', 'ib_groups')
area_members = (('users', 'users/{}'), ('classes', 'groups/{}/members'), ('groups', 'groups/{}/members'))

api_token = 'a473e92458548d66c06fe83f69831fd5'

container = Container()

from collections import defaultdict
collect_areas = defaultdict(list)

for section in sections:
	fileexists = os.path.isfile('jsons/{}.json'.format(section))

	if not fileexists:
		r = requests.get(url.format(section), params=dict(
			auth_token=api_token
			))
		try:
			json_info = r.json()
		except ValueError:
			continue
			#from IPython import embed; embed()

	else:
		with open('jsons/{}.json'.format(section)) as _f:
			json_info = json.load(_f)

	if not fileexists:
		with open('jsons/{}.json'.format(section), 'w') as _f:
			json.dump(json_info, _f, indent=4)

	if section in json_info:
		for item in json_info[section]:
			container.add(item, section)

for area, area_url in area_members:

	container_area = getattr(container, area)
	for item in container_area:
		if not item:
			continue
		this_url = area_url.format(item.id)
		this_filename = this_url.replace('/', '-')
		fileexists = os.path.isfile('jsons/{}.json'.format(this_filename))
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
			with open('jsons/{}.json'.format(this_filename)) as _f:
				json_info = json.load(_f)

		if not fileexists:
			with open('jsons/{}.json'.format(this_filename), 'w') as _f:
				json.dump(json_info, _f, indent=4)


db = Database()
for area, key in [('users', 'users'), ('groups', 'classes'), ('ib_groups', 'ib_groups')]:

	with open('jsons/'+area+'.json') as _f:
		this_json = json.load(_f)


	with DBSession() as session:
		for item in this_json[key]:
			_type = item.get('type')
			if _type == "Classes":
				_type = "Course"
			if not _type and key == 'ib_groups':
				_type = "IBGroup"

			# Convert any empty string values to None
			item = {k: v if not v == "" else None for k,v in item.items()}

			table_class = db.table_string_to_class(_type)
			instance = table_class()
			for item_key in item:
				setattr(instance, item_key, item[item_key])

			session.add(instance)

# Downloading concluded, let's popular the database
# First we need a reference to the tables.
# Uses sqlalchemy tools to poplate

Student = db.table_string_to_class('Student')
Teacher = db.table_string_to_class('Advisor')
Parent = db.table_string_to_class('Parent')
Course = db.table_string_to_class('Course')
IBGroup = db.table_string_to_class('IBGroup')

with open('jsons/users.json') as _f:
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

with open('jsons/ib_groups.json') as _f:
	this_json = json.load(_f)

for ib_group in this_json['ib_groups']:
	ib_group_id = ib_group.get('id')

	with open('jsons/groups-{}-members.json'.format(ib_group_id)) as _f2:
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

with open('jsons/groups.json') as _f:
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

for path in glob.glob('jsons/groups-*-members.json'):
	with open(path) as _f:
		this_json = json.load(_f)

	with DBSession() as session:
		course_id = re.match('jsons/groups-(\d+)-members.json', path).group(1)
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

