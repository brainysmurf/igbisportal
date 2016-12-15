from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from portal.db import Database, DBSession
db = Database()

from sqlalchemy.orm import joinedload
import json, gns

@view_config(route_name='reports_hub', renderer='{}:templates/reports_hub.pt'.format('frontend'), http_cache=0)
def reports_hub(request):
	mb_user = request.session.get('mb_user', None)

	if not mb_user:
		return HTTPForbidden()
	elif mb_user.type.startswith('Advisor') or mb_user.type == 'Account Admins':
		# let them in
		pass
	else:
		return HTTPForbidden()

	# Get all the students in elementary:
	with DBSession() as session:
		statement = session.query(db.table.Student)
		elementary_students = [s for s in statement.all() if 'PYP' in ",".join([g.program.upper() for g in s.ib_groups])]

	# pass data for the js side
	autocomplete_source = json.dumps(
		[
			{'id':student.id, 'value':student.first_nickname_last} \
				for student in elementary_students
		]
	)

	return dict(
		title="Reports Hub (elementary only at the moment)",
		students=elementary_students,
		auto_complete_source=autocomplete_source,
		api_token= gns.config.managebac.api_token
	)