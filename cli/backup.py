"""
Backup the files of the portal server
"""

# Import the built-in packages
import os
import gns
import urllib.request as req

# Import the open-source package
from smb.SMBHandler import SMBHandler

# Read in the information needed to connect to the external server
# All of these are specified in settings.ini file
# which is not version controlled
username = gns.config.backup.username
password = gns.config.backup.password
url = gns.config.backup.url.format(username=username, password=password)
backup_files = gns.config.backup.files

# Set up the transaction to the external server
connection = req.build_opener(SMBHandler)

# Loop through file that needs to be backed up...
for backup_file in backup_files.split(' '):

	# ... derive the full path to the file
	full_path = os.path.join(gns.config.backup.path, backup_file)

	# ... open the file
	with open(full_path, 'rb') as file_fh:

		# ... attempt to connect the external file and copy the data
		try:
			url_including_file_path = os.path.join(url, backup_file)
			fh = connection.open(url, data = file_fh)
			fh.close()
		except Exception as e:
			# ... if there is an exception, output it
			print(e)

	# repeat for



