import requests

options = {
    'secret': 'phillies',
    'human_columns': False,
    'columns': ['student_id', 'first_nickname_last', 'class_grade', 'parent_email_1']   # 'health_information', 'parent_contact_info', 'emergency_info',
}

#url = 'http://portal.igbis.edu.my/api/students'
url = 'http://localhost:6543/api/students'
result = requests.post(url, json=options)
json = result.json()

path = '/tmp/destinyoutput.txt'

import csv

with open(path, 'w') as _f: 
	csv_writer = csv.writer(_f)
	csv_writer.writerow(json['columns'][0])
	for student_info in json['data']:		
		csv_writer.writerow([i.encode('utf-8') if hasattr(i, 'encode') else str(i) for i in student_info])
