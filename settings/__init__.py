
"""
Implements ability to use settings.ini file, access with config_ routines
Also sets up our logger stuff
"""
import os
import sys
import ConfigParser

current_working_list = os.path.abspath(os.path.join(__file__, os.pardir)).split(os.sep)

# Look through every parent folder, looking for first settings.ini files
settings_list = []
while current_working_list:
    here = "/".join(current_working_list)
    if not here:
        break
    settings_list.append( here + '/settings.ini' )
    current_working_list.pop(-1)

settings = ConfigParser.ConfigParser(defaults={'dry_run':True, 'verbose':True})
results = settings.read(settings_list)
if not results:
    print("Some error occurred when attempting to find settings.ini file...exiting")
    exit()

def get_setting(section, attribute):
    """ returns None if not present, otherwise returns its value """
    try:
        if not settings.has_section(section):
            requires_setting(section, attribute)
            return None
        if section in ['DEFAULTS', 'DEBUGGING']:
            return settings.getboolean(section, attribute)
        else:
            return settings.get(section, attribute)
    except ConfigParser.NoOptionError:
        requires_setting(section, attribute)   # Required for us
        return None

def config_get_logging_level():
    return get_setting('LOGGING', 'log_level')

def requires_setting(section, attribute):
    """ Declare your settings needs this way, opt-in """
    if not settings.has_section(section):
        raise Exception("I require a section called {}, but no such section in settings.ini file".format(section))
    try: 
        settings.get(section, attribute)
    except ConfigParser.NoOptionError:
        raise Exception("I require '{}' attribute in {} section, no such attribute in settings.ini file".format(attribute, section))

# setup a few loggers
import logging
path_to_logging = get_setting('DIRECTORIES', 'path_to_logging') + '/'
#used to keep this in a file, let's just set it up right, shall we?
log_level = get_setting('LOGGING', 'log_level')
numeric_level = getattr(logging, log_level.upper())
if numeric_level is None:
    raise ValueError('Invalid log level: {}'.format(loglevel))

import datetime
path_to_logging += str(datetime.datetime.now().isoformat())
logging.basicConfig(filename=path_to_logging, filemode='a+', level=numeric_level)

if sys.stdout.isatty():
    # running with an attached terminal, automatically
    # set stdout debugging to full verbosity
    root = logging.getLogger()
    stdout_level = logging.DEBUG
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    root.addHandler(stdout_handler)

__all__ = [requires_setting, logging]
