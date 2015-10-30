"""
Read in info from CSV file and update the database appropriately
"""
import csv
from portal.db import Database, DBSession
db = Database()
import click

Students = db.table_string_to_class('student')
MedInfo = db.table_string_to_class('med_info')

from sqlalchemy.orm.exc import NoResultFound

from portal.db.UpdaterHelper import updater_helper

# Interface to the database
updater = updater_helper.update_or_add

class OA_Medical_Importer:

	def __init__(self, path):
		self.path = path

	@classmethod
	def from_file(cls, path):
		me = cls(path)
		return me

	@classmethod
	def from_api(cls):
		me = cls(None)
		return me

	def read_in_from_file(self):
		with open(self.path, 'rb') as _file:
			reader = csv.reader(_file, dialect='excel')
			headers = reader.next()

			translate_headers = lambda x: x.replace(' ', '_').replace('/', '_').replace('-', '')
			headers = [translate_headers(x) for x in headers]

			for row in reader:
				# Get the student info first and then go through the items
				student_id = row[0]
				if not student_id:
					click.echo("Student info with no student_id? {}".format(":".join(row)))
					continue
				with DBSession() as session:
					try:
						student = session.query(Students).filter_by(student_id=student_id).one()
					except NoResultFound:
						student = None
				if not student:
					click.echo('Student not found {}'.format(student_id))
					continue

				obj = MedInfo()
				obj.id = student.id

				for i in range(1, len(headers)):
					header = headers[i]
					item = row[i]
					setattr(obj, header, item)

				updater(obj)

	def read_in_from_api(self):
		with open(self.path, 'rb') as _file:
			reader = csv.reader(_file, dialect='excel')
			headers = reader.next()

			translate_headers = lambda x: x.replace(' ', '_').replace('/', '_').replace('-', '')
			headers = [translate_headers(x) for x in headers]

			for row in reader:
				# Get the student info first and then go through the items
				student_id = row[0]
				if not student_id:
					click.echo("Student info with no student_id? {}".format(":".join(row)))
					continue
				with DBSession() as session:
					try:
						student = session.query(Students).filter_by(student_id=student_id).one()
					except NoResultFound:
						student = None
				if not student:
					click.echo('Student not found {}'.format(student_id))
					continue

				obj = MedInfo()
				obj.id = student.id

				for i in range(1, len(headers)):
					header = headers[i]
					item = row[i]
					setattr(obj, header, item)

				updater(obj)


	def read_in(self):

		if self.path:
			self.read_in_from_file()
		else:
			self.read_in_from_api()

if __name__ == "__main__":
	read_in()