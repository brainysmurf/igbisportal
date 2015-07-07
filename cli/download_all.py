from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
import pdfkit

import requests

database = Database()
Students = database.table_string_to_class('Student')
Parents = database.table_string_to_class('Parent')
PrimaryReport = database.table_string_to_class('primary_report')

class DoIt:


	def __init__(self, one_student=None):	
		if one_student:
			self.filter = Students.student_id == one_student
		else:
			self.filter = None

	def go(self):
		term_id = 27808

		base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download?api_token={api_token}'

		import portal.settings as settings
		import gns

		api_token = settings.get('MANAGEBAC', 'mb_api_token')

		with DBSession() as session:			
			if self.filter is not None:
				students = session.query(Students).filter(self.filter).order_by(Students.first_name).all()
			else:
				students = session.query(Students).order_by(Students.first_name).all()

			for student in students:

				try:
					report = session.query(PrimaryReport).filter_by(id=student.id)
				except NoResultFound:
					continue

				r = requests.get(base_url.format(student_id=student.id, api_token=api_token))

				if r.status_code != 200:
					print("Nope: {}, {}".format(student.id, r.status_code))

	def dates(self):
		term_id = 27808

		base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download?api_token={api_token}'

		import portal.settings as settings
		import gns

		api_token = settings.get('MANAGEBAC', 'mb_api_token')

		with DBSession() as session:			
			if self.filter is not None:
				parents = session.query(Parents).filter(self.filter).all()
			else:
				parents = session.query(Parents).all()

			for parent in parents:
				parent.google_account_sunset('1 month')
		print('Done!')


if __name__ == "__main__":

	#do = DoIt()  # everyone
	#do = DoIt(one_student="20280001")  # Arlo: Early Years
	#do = DoIt(one_student='20250002')   # Zilin
	#do = DoIt(one_student="20240002")   # Calvin
	#do = DoIt(one_student='20220011')
	#do = DoIt(one_student="20280018")   # Narissa
	#do = DoIt(one_student="20250010")    # Bryce

	student_ids = ["20290010", "20280005", "20250008", "20240014", "20230008", "20220001", "20220011", "20220009"]
	for sid in student_ids:
		do = DoIt(one_student=sid)
		do.go()

	#do.dates()
	do.go()
