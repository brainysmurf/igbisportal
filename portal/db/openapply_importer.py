"""
Read in info from CSV file and update the database appropriately
"""
import csv
from portal.db import Database, DBSession
db = Database()

Students = db.table_string_to_class('student')
MedInfo = db.table_string_to_class('med_info')

from sqlalchemy.orm.exc import NoResultFound

from portal.db.UpdaterHelper import updater_helper

updater = updater_helper.update_or_add

def from_scratch():
	from portal.db import metadata, engine
	metadata.create_all(engine)

def read_in():
	path = 'emergency.csv'
	with open(path, 'rb') as _file:
		reader = csv.reader(_file, dialect='excel')
		headers = reader.next()

		translate_headers = lambda x: x.replace(' ', '_').replace('/', '_').replace('-', '')
		headers = [translate_headers(x) for x in headers]

		for row in reader:
			# Get the student info first and then go through the items
			student_id = row[0]
			with DBSession() as session:
				try:
					student = session.query(Students).filter_by(student_id=student_id).one()
				except NoResultFound:
					student = None
			if not student:
				print('student not found {}'.format(row))
				continue

			obj = MedInfo()
			obj.id = student.id

			for i in range(1, len(headers)):
				header = headers[i]
				item = row[i]
				setattr(obj, header, item)

			updater(obj)


if __name__ == "__main__":
	from_scratch()
	read_in()