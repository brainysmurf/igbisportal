from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )

import redis
import json

r = redis.Redis('localhost')

@view_config(route_name='auditlog', renderer='templates/auditlog.pt')
def auditlog(request):
    return dict(project='test')

@view_config(route_name='auditlog_data', renderer='json')
def auditlog_data(request):
    data = {'data':[]}
    for serialized_item in r.smembers('/admin/audit?page={}'):
        python_list = json.loads(serialized_item)
        data['data'].append(python_list)
    return data

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'frontend'}

@view_config(route_name='poll', renderer='json')
def poll(request):
    return {'success':True}

@view_config(route_name='test_polling', renderer='templates/polling.pt')
def test_polling(request):
    return {'project':'frontend'}

@view_config(route_name='test_polling', renderer='templates/polling.pt')
def user_info(request):
    return(api_key='a473e92458548d66c06fe83f69831fd5')

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_frontend_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

