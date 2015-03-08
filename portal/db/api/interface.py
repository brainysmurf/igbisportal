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
import portal.settings as settings
import gns

class APIDownloader(object):
	"""
	Responsible for initial downloads from API
	"""	

	def __init__(self, prefix=None, api_token=None, lazy=True, verbose=False):
		"""
		Sent in optional params can override settings.ini, useful for debugging
		"""
		if not prefix:
			settings.get('MANAGEBAC', 'mb_prefix', required=True)
			self.prefix = gns.settings.mb_prefix
		else:
			settings.override('MANAGEBAC', 'mb_prefix', prefix)

		self.url = gns('https://{settings.mb_prefix}.managebac.com/api/{{uri}}')
		# TODO: Make this a setting
		if not api_token:
			self.api_token = settings.get('MANAGEBAC', 'mb_api_token', required=True)
		else:
			settings.override('MANAGEBAC', 'mb_api_token', api_token)

		settings.get('MANAGEBAC', 'sections', required=True)
		settings.get('MANAGEBAC', 'sections_with_members', required=True)

		self.section_urls = {}
		for gns.section in gns.settings.sections:
			value = settings.get('MANAGEBAC', gns('{section}_section_url'))
			if value:
				self.section_urls[gns.section] = value

		self.container = Container()

		settings.get('DIRECTORIES', 'path_to_jsons', required=True)
		settings.setup_verbosity(self)

		if not lazy:
			# Immediately do our thang.
			self.download(overwrite=True)

	def build_json_path(self, *args):
		"""
		Pass it a variable number of parameters to build the path to json
		"""
		gns.tmp = "".join(args)
		return gns("{settings.path_to_jsons}/{tmp}")

	def write_to_disk(self, obj, path):
		self.default_logger('Writing to disk @ {}'.format(path))
		with open(path, 'w') as _f:
			json.dump(obj, _f, indent=4)

	def download(self, overwrite=False):
		"""
		Downloads known paths from api and places it onto directories
		"""
		if overwrite:
			self.default_logger('Overwriting')
			if os.path.isdir(self.build_json_path()):
				import shutil
				self.default_logger("Removing everything now")
				shutil.rmtree(self.build_json_path())
			else:
				pass

		if not os.path.isdir(self.build_json_path()):
			self.default_logger('Making the json directory')
			os.mkdir(self.build_json_path())

		for gns.section in gns.settings.sections:
			self.default_logger(gns('On section {section}'))
			file_path = self.build_json_path(gns.section, '.json')
			fileexists = os.path.isfile(file_path)

			if not fileexists:
				url = self.url.format(uri=gns.section)
				self.default_logger('Downloading {}'.format(url))

				r = requests.get(url, params=dict(
					auth_token=self.api_token
					))
				try:
					if not r.ok:
						self.default_logger('Download request did not return "OK"')
					json_info = r.json()
				except ValueError:
					self.default_logger('Invalid json after download. Oops?')

			else:
				with open(file_path) as _f:
					json_info = json.load(_f)

			if not fileexists:
				self.write_to_disk(json_info, file_path)

			if gns.section in json_info:
				self.default_logger('Section found in json')
				for item in json_info[gns.section]:
					self.container.add(item, gns.section)

		for gns.section in gns.settings.sections:
			section_url = self.section_urls.get(gns.section)
			if not section_url:
				self.default_logger(gns('Skipping section {section}'))
				continue

			container_area = getattr(self.container, gns.section)
			self.default_logger(gns('On section {section}'))

			for item in container_area:
				if not item:
					self.default_logger('Skipping because item is None')
					continue
				this_url = section_url.format(id=item.id)
				this_filename = this_url.replace('/', '-')
				file_path = self.build_json_path(this_filename, '.json')
				fileexists = os.path.isfile(file_path)
				if not fileexists:
					self.default_logger('Downloading {}'.format(this_filename))
					try:
						r = requests.get(self.url.format(uri=this_url), params=dict(
						auth_token=self.api_token
						))
					except requests.exceptions.SSLError:
						continue
					try:
						json_info = r.json()
					except ValueError:
						self.default_logger('Trouble with json')
						continue

				else:
					self.default_logger('Found file {}, reading in json info'.format(file_path))
					with open(file_path) as _f:
						json_info = json.load(_f)

				if not fileexists:
					self.write_to_disk(json_info, file_path)		


if __name__ == "__main__":

	go = Downloader()

	go.download(overwrite=False)
	go.setup_database()





