import scrapy   
from scrapy.http.cookies import CookieJar
from auditlog.settings import OPEN_APPLY_URL, OPEN_APPLY_LOGIN
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
    allowed_domains = [OPEN_APPLY_URL]
    start_urls = [
        OPEN_APPLY_LOGIN
    ]

    def warning(self, log):
        scrapy.log.msg(log, level=scrapy.log.WARNING)

    def path_to_url(self, path):
        return OPEN_APPLY_URL + path

    def parse(self, response):
        self.cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        self.cookieJar.extract_cookies(response, response.request)

        self.warning("Logging in!")
        login_request = scrapy.FormRequest.from_response(
            response,
            formdata={'user[email]': 'adam.morris@igbis.edu.my', 'user[password]': 'M0kalB3t'},
            callback=self.after_login,
            dont_filter=True  # because it's the same form
        )
        return login_request

    def after_login(self, response):
        # check login succeed before going on
        if "authentication failed" in response.body:
            self.warning("Authentication failed", level=log.WARNING)            
            return

        # Automagically route to method with same name as class
        name_to_dispatch = convert(self.__class__.__name__)
        method = getattr(self, name_to_dispatch)
        if method:
            return method()
        else:
            self.warning("No method {} defined for class {}.".format(name_to_dispatch, self.__class__.__name__))