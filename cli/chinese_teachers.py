# MENU thingie for me to make it easy to maintain chinese teacher lists
#

from portal.db import Database, DBSession
db = Database()
Students = db.table.Student
Teachers = db.table.Teacher
import click

if __name__ == "__main__":

	grade = None

	build = set()
	students = []

	while True:

		if grade == None:
			grade = click.prompt("Grade")
			with DBSession() as session:

				statement = session.query(Students).filter_by(grade=grade, archived=False).order_by(Students.nickname_last_studentid)
				students = statement.all()

		i = 0
		for student in students:
			student.index = i
			click.echo("{} {}".format(i+1, student.nickname_last_studentid))
			i += 1
		click.echo('G: Change Grade')
		choice = click.prompt('')

		if choice.lower() == 'g':
			grade = None

		elif choice.lower() == 'clear':
			click.echo("CLEAR (y/N)")
			char = click.getchar()
			if char.lower() == 'y':
				build = set()
		elif choice.lower() == 'b':
			click.echo(",".join([str(b) for b in list(build)]))
			click.getchar()
		elif choice.isdigit():
			student = students[int(choice)-1]
			check = click.prompt(student.nickname_last_studentid + ' (Y/n)')
			if check.lower() != 'n':
				build.add(student.id)
				del students[student.index]

				click.echo('Added')
				click.getchar()

