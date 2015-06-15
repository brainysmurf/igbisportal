"""
Executes gam code without having to go back to the system
Since gam isn't organized into function, we have to do the below hackish thing

Init GamWrapper to get class that implements details
It only imports gam once, and then after that reloads
and sets sys.argv all the while

Captures and parses output into a useful json
"""

import shlex
import click
import sys
from cStringIO import StringIO
import json
import pprint

class GamWrapper:
	def __init__(self, path, verbose=None):
		"""
		Gam requires the path to be passed along in the command line
		"""
		self.path = path
		self.__gamimport__ = None
		self.verbose = verbose

	def parse_gam_stdout(self, stdout=None, stderr=None):
		"""
		Rather tedious: Looked through the gam.py file and looked for patterns
		If an error occurs, there's an .error in the object
		"""
		j = dict(error=None)
		if 'ERROR:' in stdout.upper():
			j['error'] = stdout[4:]
		if stderr:
			j['error'] = stderr
		j['raw'] = dict(stdout=stdout, stderr=stderr)
		self.verbose and pprint.pprint(j)
		return j

	def call_gam(self, cmd):
		# manually set sys.argv
		# First command should be "gam" so let's change the path
		cmd = cmd.replace('gam ', "{} ".format(self.path))
		self.verbose and click.echo(cmd)
		sys.argv = shlex.split(cmd)

		# Manually set up to capture stdout and stderr
		# since gam is not importable, we have to do it this way
		# We are messing around with stdout and stderr, so let's be careful
		# Sanity checks!
		stdout_backup = sys.stdout
		stderr_backup = sys.stderr
		try:
			sys.stdout = StringIO()
			sys.stderr = StringIO()

			# import or reload the module, which reads in the sys.argv
			# we don't want to import and then just reload
			# just import once, then after that, reload
			if self.__gamimport__ is None:
				# first gam comes from setuptools, second is the actual module within
				from gam import gam as gamimport # importing gam for first time, which will run the commands
				self.__gamimport__ = gamimport
			else:
				reload(self.__gamimport__)  # importing after that, which runs the commands

			# now, capture any output
			_stdout = sys.stdout.getvalue().strip('\n')
			_stderr = sys.stderr.getvalue().strip('\n')

		except:  # this except / raise without an "Exception as e" gives a much cleaner traceback
			sys.stdout.close()
			sys.stdout.close()

			sys.stdout = stdout_backup
			sys.stderr = stderr_backup
			raise

		sys.stdout.close()
		sys.stdout.close()
		sys.stdout = stdout_backup
		sys.stderr = stderr_backup

		# process the results
		return self.parse_gam_stdout(_stdout, _stderr)

	def loop_from_stdin(self):
		cmd = click.prompt('')

		# click formats it in a way where we have to encode it manually here
		result = self.call_gam(cmd.encode('utf-8'))

		if result.get('error'):
			click.secho(result.get('error'), fg='red')

		self.verbose and click.echo(result)

		# rinse, and repeat, until ctrl-C
		self.loop_from_stdin()

if __name__ == "__main__":
	# Test:

	import gns
	from portal.settings import get
	gam_path = get('DIRECTORIES', 'path_to_gam')
	print(gam_path)
	click.secho('Gam wrapper, baby', fg='green')

	gw = GamWrapper(gam_path, verbose=True)

	try: 
		gw.loop_from_stdin()	
	except click.exceptions.Abort:
		click.echo()  # newline
		pass