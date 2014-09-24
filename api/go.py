import requests
import redis
from model import Abstract, Container

#database = redis.Redis('localhost')
class DataBase(object):
	def hset(self, _hash, key, value):
		pass
		#print(_hash, key, value)
database = DataBase()

PREFIX = 'igbis2014'
url = 'https://igbis.managebac.com/api/{}'
sections = ('users', 'classes', 'groups/{}/members')
api_token = 'a473e92458548d66c06fe83f69831fd5'

container = Container()

for section in sections:
	print(url.format(section))
	r = requests.get(url.format(section), params=dict(
		auth_token=api_token
		))
	if not r.ok:
		continue

	json = r.json()

	if section in json:
		for item in json[section]:
			container.add(item)
	from IPython import embed; embed()