"""
The file lets me sort out the model for myself
1) Downloads info that is available via API into files
2) Puts it into database

Excuse the mess, it works well enough but isn't exactly clear what's happening
In particular errors aren't handled (FIXME)
"""
from portal.db.api.model import Container
import json
import os.path
import re, sys
from functools import partial
import requests
import gns

class APIDownloader(object):
	"""
	Responsible for initial downloads from API
	"""	

	def __init__(self, prefix=None, api_token=None, lazy=True, verbose=False):
		"""
		Sent in optional params can override settings.ini, useful for debugging
		"""
		self.debug = True

		self.prefix = prefix or gns.config.managebac.prefix

		self.url = 'https://{prefix}.managebac.com/api/{{uri}}'.format(prefix=self.prefix)
		self.api_token = api_token or gns.config.managebac.api_token

		self.section_urls = {}
		for section in gns.config.managebac.sections.split(','):
			try:
				value = getattr(gns.config.managebac, '{}_section_url'.format(section))
				if value:
					self.section_urls[section] = value
			except AttributeError:
				pass

		self.container = Container()

		if not lazy:
			# Immediately do our thang.
			self.download(overwrite=True)
			self.open_apply_download(overwrite=True)

	def default_logger(self, *args, **kwargs):
		#print(args)   # uncomment this line
		pass

	def download_get(self, *args, **kwargs):
		print("Downloading via api: {}".format(args[0]))
		return requests.get(*args, **kwargs)

	def build_json_path(self, *args):
		"""
		Pass it a variable number of parameters to build the path to json
		"""
		gns.tmp = "".join(args)
		return gns("{config.paths.jsons}/{tmp}")

	def write_to_disk(self, obj, path):
		self.debug and self.default_logger('Writing to disk @ {}'.format(path))
		with open(path, 'w') as _f:
			json.dump(obj, _f, indent=4)

	def managebac_users_download(self):
		api_token = gns.config.managebac.api_token
		url = gns.config.managebac.api_url + '/users'
		r = self.download_get(url, params=dict(
				auth_token=api_token,
			))
		if not r.ok:
			print("Failed")
		else:
			json_obj = r.json()
			path = self.build_json_path('users', '.json')
			self.write_to_disk(json_obj, path)

	def open_apply_download(self, overwrite=False):
		"""
		TODO: Make overwrite meaningful
		"""
		api_token = gns.config.openapply.api_token
		url = "{}/{{uri}}".format(gns.config.openapply.api_url)
		url = url.format(uri='students')

		since_id = 0
		compiled_json_obj = {'students':[], 'parents':[]}

		while since_id >= 0:

			r = self.download_get(url, params=dict(
				auth_token=api_token,
				count=10,
				since_id=since_id
				))

			if not r.ok:
				self.debug and self.default_logger('Download request did not return "OK"')
				since_id = -1
			else:
				json_info = r.json()
				# make since_id the id for the last id passed
				these_students = json_info.get('students')
				these_links = json_info.get('linked')
				if not these_students:
					since_id = -1
				else:
					since_id = these_students[-1].get('id')
					if these_students:
						compiled_json_obj['students'].extend(these_students)
					if these_links:
						compiled_json_obj['parents'].extend(these_links.get('parents'))

		path = self.build_json_path('open_apply_users', '.json')
		self.write_to_disk(compiled_json_obj, path)

	def download(self, overwrite=False):
		"""
		Downloads known paths from api and places it onto directories
		"""
		if overwrite:
			self.debug and self.default_logger('Overwriting')
			if os.path.isdir(self.build_json_path()):
				import shutil
				self.debug and self.default_logger("Removing everything now")
				shutil.rmtree(self.build_json_path())
			else:
				pass

		if not os.path.isdir(self.build_json_path()):
			self.debug and self.default_logger('Making the json directory')
			os.mkdir(self.build_json_path())

		for gns.section in gns.config.managebac.sections.split(','):
			self.debug and self.default_logger(gns('On section {section}'))
			file_path = self.build_json_path(gns.section, '.json')
			fileexists = os.path.isfile(file_path)

			if not fileexists:
				url = self.url.format(uri=gns.section)
				self.debug and self.default_logger('Downloading {}'.format(url))

				r = self.download_get(url, params=dict(
					auth_token=self.api_token
					))
				try:
					if not r.ok:
						self.debug and self.default_logger('Download request did not return "OK"')
					json_info = r.json()
				except ValueError:
					self.debug and self.default_logger('Invalid json after download. Oops?')

			else:
				with open(file_path) as _f:
					json_info = json.load(_f)

			if not fileexists:
				self.write_to_disk(json_info, file_path)

			if gns.section in json_info:
				self.debug and self.default_logger('Section found in json')
				for item in json_info[gns.section]:
					self.container.add(item, gns.section)

		for gns.section in gns.config.managebac.sections.split(','):
			section_url = self.section_urls.get(gns.section)
			if not section_url:
				self.debug and self.default_logger(gns('Skipping section {section}'))
				continue

			container_area = getattr(self.container, gns.section)
			self.debug and self.default_logger(gns('On section {section}'))

			for item in container_area:
				if not item:
					self.debug and self.default_logger('Skipping because item is None')
					continue
				this_url = section_url.format(id=item.id)
				this_filename = this_url.replace('/', '-')
				file_path = self.build_json_path(this_filename, '.json')
				fileexists = os.path.isfile(file_path)
				if not fileexists:
					self.debug and self.default_logger('Downloading {}'.format(this_filename))
					try:
						r = self.download_get(self.url.format(uri=this_url), params=dict(
						auth_token=self.api_token
						))
					except requests.exceptions.SSLError:
						continue
					try:
						json_info = r.json()
					except ValueError:
						self.debug and self.default_logger('Trouble with json')
						continue

				else:
					self.debug and self.default_logger('Found file {}, reading in json info'.format(file_path))
					with open(file_path) as _f:
						json_info = json.load(_f)

				if not fileexists:
					self.write_to_disk(json_info, file_path)		


if __name__ == "__main__":

	go = APIDownloader()

	go.open_apply_download(overwrite=True)





