HEADERS = ['Student', 'Email']
SUFFIX = '-1617'

from portal.db import DBSession, Database
from sqlalchemy.orm import joinedload
import re

class StudentLine:

	def __init__(self, student_email, student_class):
		self.student_email = student_email
		self.student_class = student_class

	def __call__(self):
		return ",".join([self.student_email, self.student_class])


def student():

	db = Database()
	with DBSession() as session:

		statement = session.query(db.table.Student).\
			options(joinedload('classes'))

		output = []

		for student in statement.all():
			for class_ in student.classes:
				if student.email and class_.uniq_id:
					uniq_id = "{}{}".format(class_.uniq_id, SUFFIX)
					output.append(StudentLine(student_email=student.email, student_class=uniq_id))

		#from IPython import embed;embed()

		output = sorted(output, key=lambda obj: (obj.student_email, obj.student_class))
		output.insert(0, StudentLine(student_email='Student', student_class='Class'))

		with open('/tmp/student.csv', 'w') as f_:
			f_.write('\n'.join([student_line() for student_line in output]))


class ClassLine:

	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def __call__(self):
		return ",".join([
			self.mailbox,
			self.name,
			self.description,
			self.teacher,
			self.subject_folders,
			self.student_sites,
			self.student_blogs,
			self.class_calendar
			]
		)


def classes():
	db = Database()

	with DBSession() as session:

		statement = session.query(db.table.Teacher).\
			options(joinedload('classes'))

		output = []

		for teacher in statement.all():
			for class_ in teacher.classes:
				if teacher.email and class_.uniq_id:
					uniq_id = "{}{}".format(class_.uniq_id, SUFFIX)
					name = class_.name.replace("IB MYP", '').replace('IB DP', '').replace('IB PYP', '').replace('Arts -', '').strip()
					name = re.sub('\(.*?\)', '', name).strip()
					name = re.sub('  \d$', '', name)
					description = "{}:{}".format(class_.grade, name)
					output.append(
						ClassLine(
							mailbox=uniq_id,
							name=uniq_id, 
							description=description,
							teacher=teacher.email,
							subject_folders=class_.name,
							student_sites='any',
							student_blogs='any',
							class_calendar=uniq_id
						)
					)

		output = sorted(output, key=lambda obj: (obj.mailbox, obj.teacher))
		output.insert(0, ClassLine(							
			mailbox="Mailbox",
			name="Name", 
			description="Description",
			teacher="Teacher",
			subject_folders="Subject Folder",
			student_sites='Student Sites',
			student_blogs='Student Blogs',
			class_calendar='Class Calendar')
		)
		with open('/tmp/classes.csv', 'w') as f_:
			f_.write('\n'.join([student_line() for student_line in output]))


if __name__ == '__main__':

	student()
	classes()