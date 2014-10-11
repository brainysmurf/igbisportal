import json

with open('jsons/groups.json') as _f:
	this_json = json.load(_f)

for course in this_json['classes']:
	print course.get('id')