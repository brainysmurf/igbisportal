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
        # FIXME: The model should have a flag of some sort instead of looking at the ib_groups stuff like this
        elementary_students = [s for s in statement.all() if 'PYP' in ",".join([g.program.upper() for g in s.ib_groups])]

    # pass data for the js side
    individual_autocomplete_source = json.dumps(
        [
            {'id':student.id, 'value':student.first_nickname_last} \
                for student in elementary_students
        ]
    )

    with DBSession() as session:
        statement = session.query(db.table.Course).filter(db.table.Course.name.like('%PYP%'))
        pyp_homerooms = statement.all()

    pyp_homerooms_autocomplete_source = json.dumps(
        [
            {'id': course.id, 'value': course.name} \
                for course in pyp_homerooms
        ]
    )

    update_section = mb_user.type == 'Account Admins'

    return dict(
        title = "Reports Hub (elementary only at the moment)",
        students = elementary_students,
        individuals_autocomplete_source = individual_autocomplete_source,
        pyp_homerooms_autocomplete_source = pyp_homerooms_autocomplete_source,
        update_section = mb_user.type == 'Account Admins',
        api_token = gns.config.managebac.api_token
    )