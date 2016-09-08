
from portal.db import Database, DBSession
from sqlalchemy.orm import joinedload
database = Database()
Students = database.table_string_to_class('Student')


class Exporter:

	def __init__(self):
		pass


	def parent_emails(self, **filter_by):

		with DBSession() as session:
			statement = session.query(Students).options(joinedload('parents')).filter_by(**filter_by)

			for item in statement.all():
				for parent in item.parents:
					print(parent.email)

if __name__ == "__main__":

	exporter = Exporter()

	exporter.parent_emails(class_year=10)

