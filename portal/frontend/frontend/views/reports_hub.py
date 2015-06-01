from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from portal.db import Database, DBSession
db = Database()

import json

Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')
Enrollments = db.table_string_to_class('enrollment')
Assignments = db.table_string_to_class('assignment')
ReportComments = db.table_string_to_class('report_comments')
PrimaryReport = db.table_string_to_class('primary_report')
Courses = db.table_string_to_class('course')
Absences = db.table_string_to_class('PrimaryStudentAbsences')
HRTeachers = db.table_string_to_class('secondary_homeroom_teachers')
GSignIn = db.table_string_to_class('google_sign_in')
UserSettings = db.table_string_to_class('user_settings')

@view_config(route_name='reports_hub', renderer='{}:templates/reports_hub.pt'.format('frontend'), http_cache=0)
def reports_hub(request):

	mb_user = request.session.get('mb_user', None)

	if not mb_user or not mb_user.type.startswith('Advisor'):
		return HTTPForbidden()

	# Get all the students in elementary:
	with DBSession() as session:
		statement = session.query(Students).filter(Students.class_year == 0)
		elementary_students = statement.all()

	autocomplete_source = \
		[{'id':student.id, 'value':'{} {} ({})'.format(student.first_name, student.last_name, student.nickname)} \
			for student in elementary_students]

	return dict(
		title="Reports Hub (elementary only at the moment)",
		students=elementary_students,
		auto_complete_source=json.dumps(autocomplete_source)
		)