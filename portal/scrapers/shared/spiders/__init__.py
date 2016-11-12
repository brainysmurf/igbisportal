"""

TODO: At the moment if login fails this is not necessarily detected
Change username_field to something that should break it to test
"""

import scrapy   
from scrapy.http.cookies import CookieJar
import gns
import re

FIRSTCAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALLCAP_RE = re.compile('([a-z0-9])([A-Z])')
def convert(name):
    """
    Converts from CamelCase to camel_case
    Stolen from http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
    """
    s1 = FIRSTCAP_RE.sub(r'\1_\2', name)
    return ALLCAP_RE.sub(r'\1_\2', s1).lower()

class Login(scrapy.Spider):
    """
    Subclass me and get the following free behaviour:
    * Logs in, printing a warning if does not authenticate
    * Routes to method with same name as class converted from CamelCase to camel_case
    """
    name = "Login"
    username_field = 'login'
    password_field = 'password'

    username = None
    password = None

    def warning(self, log):
        scrapy.log.msg(log, level=scrapy.log.WARNING)

    def parse(self, response):
        login_request = scrapy.FormRequest.from_response(
            response,
            formdata={self.username_field: self.username, self.password_field: self.password},
            callback=self.after_login,
            dont_filter=True  # because it's the same form
        )        
        return login_request

    def after_login(self, response):
        # check login succeed before going on
        if response.status != 200 or "authentication failed" in response.body_as_unicode():
            self.warning("Authentication failed", level=log.WARNING)            
            return

        # Automagically route to method with same name as class
        name_to_dispatch = convert(self.__class__.__name__)

        method = getattr(self, name_to_dispatch)
        if method:
            return method()
        else:
            self.warning("No method {} defined for class {}.".format(name_to_dispatch, self.__class__.__name__))

class OpenApplyLogin(Login):
    name = "OpenApplyLogin"
    allowed_domains = [gns.config.openapply.url]
    start_urls = [gns.config.openapply.login_url]
    username_field = 'user[email]'
    password_field = 'user[password]'

    username = gns.config.openapply.admin_username
    password = gns.config.openapply.admin_password

    def path_to_url(self, path):
        return gns.config.openapply.url + path

class ManageBacLogin(Login):
    name = "ManageBacLogin"
    allowed_domains = [gns.config.managebac.url]
    start_urls = [gns.config.managebac.login_url]

    username = gns.config.managebac.admin_username
    password = gns.config.managebac.admin_password

    def path_to_url(self, path):
        return gns.config.managebac.url + path