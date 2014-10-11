"""
Just a tool to tinker with
"""
from IPython import embed
import requests, json
prefix = 'igbis'
url = 'https://{}.managebac.com/api/{{}}'.format(prefix)
payload=dict(auth_token='a473e92458548d66c06fe83f69831fd5')
data = dict(
	type='Student',
	student_id=20220001,
	first_name='Aasiyah',
	last_name='Badlisyah',
	email='Aasiyah.Badlisyah022@igbis.edu.my'	
	)

headers = {'content-type': 'application/json'}

print('"get" or "post", with params')

post = requests.post
get = requests.get
embed()
