from db import Database, DBSession

db = Database()

Timetable = db.table_string_to_class('Timetable')
Course = db.table_string_to_class('Course')
Student = db.table_string_to_class('Student')
Enrollment = db.table_string_to_class('Enrollment')
IBGroup = db.table_string_to_class('IBGroup')
IBGroupMembership = db.table_string_to_class('IBGroupMembership')

with DBSession() as session:

	# statement = session.query(IBGroup.grade, Course.name, Student.last_name, Student.first_name, Timetable.day, Timetable.period).\
	# 	select_from(Timetable).\
	# 		join(Course, Course.id == Timetable.course_id).\
	# 		join(Enrollment, Enrollment.c.course_id == Course.id).\
	# 		join(Student, Student.student_id == Enrollment.c.student_id ).\
	# 		join(IBGroupMembership, IBGroupMembership.c.student_id == Student.student_id).\
	# 		join(IBGroup, IBGroup.id == IBGroupMembership.c.ib_group_id)

	statement = session.query(Course.grade, Course.name, Timetable.day, Timetable.period).\
		select_from(Course).\
			join(Timetable, Timetable.course_id == Course.id).\
			filter(Course.grade == "Grade 8")

every = sorted(list(statement.all()), key = lambda x: (x[2], x[3]))

rows = []

period = 0
built = {}
for item in every:
	print(item)
	if item[3] != period:
		period += 1
		if built:
			rows.append(built)
		built = {1:[], 2:[], 3:[], 4:[], 5:[]}
	else:
		day = item[2]
		print((period, item[1]))
		built[day].append(item[1])
		raw_input()
#rows.append(built)

print(rows)