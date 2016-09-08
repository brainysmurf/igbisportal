from portal.db import Database, DBSession
db = Database()
import re

Teachers = db.table_string_to_class('advisor')

with DBSession() as session:
    user = session.query(Teachers).filter(Teachers.id == 10792610).one()
    if not user:
        print(dict(message="No user in session?"))
    if not hasattr(user, 'classes'):
        print(dict(message="User doesn't have classes?"))
    data = []
    for klass in user.classes:
    	grade_str = re.search('\((.*?)\)', klass.name)
    	if grade_str:
    		str = grade_str.group(1)
    		grade_str = {'Grade 10': 10, 'Grade 11': 11, 'Grade 12': 12}.get(str, int(re.sub('[^0-9]', '', str)))
    	else:
    		grade_str = ""
        data.append( dict(name=klass.abbrev_name, sortby=(grade_str, klass.uniq_id), shortname=klass.uniq_id, link='https://igbis.managebac.com/classes/{}'.format(klass.id)) )
    for item in sorted(data, key=lambda x: x['sortby'], reverse=True):
    	print(item['name'])
