"""
Don't really understand this fully, but the below let's us do this:
import inspect
inspect.getfile(dss)
with the result of the path, which I use with configparser

c.f.
http://travisswicegood.com/2009/12/22/the-problem-with-python-namespaces-modul/
"""
import pkg_resources
pkg_resources.declare_namespace(__name__)

