from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
import pdfkit
import gns
import re
from sqlalchemy import and_

import requests

database = Database()
Students = database.table_string_to_class('Student')
Parents = database.table_string_to_class('Parent')
PrimaryReport = database.table_string_to_class('primary_report')

class DoIt:
	base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download?api_token={api_token}'

	def __init__(self, one_student=None, one_grade=None):
		if one_student:
			self.filter = Students.student_id == one_student
		elif one_grade:
			self.filter = Students.class_grade == one_grade
		else:
			self.filter = None

	def go(self, starting_from=None):
		term_id = 55880

		api_token = gns.config.managebac.api_token

		with DBSession() as session:			
			if self.filter is not None:
				students = session.query(Students).filter(self.filter).order_by(Students.grade).all()
			else:
				students = session.query(Students).filter(and_(Students.grade < 6, Students.is_archived==False, Students.student_id != None)).order_by(Students.grade).all()
				if starting_from:
					index = [i for i in range(len(students)) if students[i].student_id==starting_from]
					if index:
						index = index[0]
						students = students[index:]
					else:
						students = []

			for student in students:
				try:
					report = session.query(PrimaryReport).filter_by(id=student.id)
				except NoResultFound:
					#raw_input('no report!')
					continue

				url = self.base_url.format(student_id=student.id, api_token=api_token)
				r = requests.get(url)

				if r.status_code == 200:
					print("All is well with {}".format(student))
					#print(r.url)

				if r.status_code != 200:
					#print(url.replace('localhost', 'igbisportal.vagrant'))
					text = r.text
					message = re.findall('##(.*)##', text, re.DOTALL)
					if message:
						print(message[0])
					else:
						self.output("Nope {}: {}, {}".format(r.status_code, student.student_id, url))

	def dates(self):
		term_id = 55880

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

	def output(self, msg):
		print(msg)

class CheckIt(DoIt):

	base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download?api_token={api_token}&check=True'

	def output(self, msg):
		pass

if __name__ == "__main__":

	# Departing
	# do = DoIt(one_student="20260001")   # kayla
	# do.go()
	# do = DoIt(one_student="20280020")	# andre
	# do.go()
	# do = DoIt(one_student="20290015")	# asha
	# do.go()
	# do = DoIt(one_student="20290024")   # yazuiki
	# do.go()
	# do = DoIt(one_student="20280003")	# freya
	# do.go()
	# do = DoIt(one_student="20300002") 	# victor	
	# do.go()

	# 4T
	#do = DoIt(one_student="20300002")

	#do = DoIt()
	do = DoIt(one_student="20300015")
	do.go()

	#Shah Reza	Shahabudin	20230006	Grade 5 NOT LISTED
	#Seth	Lee	20040003	  NOT LISTED
	# Neve	Riseley	20240006	Grade 3  NOT LISTED
	#Lachlan	Riseley	20270006	Kindergarten NOT LISTED
	#Jing Wen	Lee	20250005	Grade 2 NOT LISTED

	#do = DoIt()
	# NEED
	# do = DoIt(one_student="20280009")  # Ryan
	# do.go()
	# do = DoIt(one_student="20280024")
	# do.go()
	# do = DoIt(one_student="20280027")
	# do.go()
	# do = DoIt(one_student="20280016")
	# do.go()
	# do = DoIt(one_student="20280026")
	# do.go()
	# do = DoIt(one_student="20280017")
	# do.go()
	# do = DoIt(one_student="20270017")
	# do.go()
	# do = DoIt(one_student="20250010")
	# do.go()
	# do = DoIt(one_student="20230011")
	# do.go()
	# do = DoIt(one_student="20240019")
	# do.go()
	# do = DoIt(one_student="20240016")
	# do.go()

	# EARLY YEARS
	# do = DoIt(one_student="20300012")
	# do.go()
	# do = DoIt(one_student="20290016")
	# do.go()
	# do = DoIt(one_student="20300014")
	# do.go()
	# do = DoIt(one_student="20300007")
	# do.go()
	# do = DoIt(one_student="20300010")
	# do.go()
	# do = DoIt(one_student="20290004")
	# do.go()
	# do = DoIt(one_student="20290014")
	# do.go()
	#do = CheckIt()
	#do = DoIt(one_student="20300014")   # Early Years 1
	#do = DoIt(one_student="20290010")   # Tea
	#do = DoIt(one_student="20240023")   # Jack Dabb
	#do.go()


	# student_ids = ["20290010", "20280005", "20250008", "20240014", "20230008", "20220001", "20220011", "20220009"]
	# for sid in student_ids:
	# 	do = DoIt(one_student=sid)
	# 	do.go()

	#do.dates()
	#do.go()
