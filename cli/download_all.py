from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
import pdfkit

import requests

database = Database()

Students = database.table_string_to_class('Student')
PrimaryReport = database.table_string_to_class('primary_report')
term_id = 27807

base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download'

with DBSession() as session:

	students = session.query(Students).order_by(Students.first_name).all()

	for student in students:

		try:
			report = session.query(PrimaryReport).filter_by(id=student.id)
		except NoResultFound:
			continue

		r = requests.get(base_url.format(student_id=student.id))

		if r.status_code != 200:
			print("Nope: {}".format(student.id))
