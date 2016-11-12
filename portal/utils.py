# -*- coding: utf-8 -*-

"""
Utility for converting raw text into html-friendly strings
"""

from xml.sax.saxutils import escape, unescape
import datetime

html_escape_table = {
	u'“': "&ldquo;",
	u"”": "&rdquo;",
	u"‘": "&lsquo;",
	u"’": "&rsquo;",
	"<": "&lt;",
	'>': "&gt;",
	'1/10': '<span style="font-size:70%;"><sup>1</sup>&frasl;<sub>10</sub></span>',
	u'–': '-',
	u'½': '1&frasl;2',
	u'⅓': '1&frasl;3',
	u'¼': '1&frasl;4',
}

html_unescape_table = {v:k for k, v in html_escape_table.items()}

def get_this_academic_year():
    now = datetime.date.today()
    year, month = int(str(now.year)[2:]), now.month
    # FIXME: This only works in any and all cases if enrollment date is August 1
    academic_year = year if month < 8 else year + 1
    return academic_year

def get_year_of_graduation(grade):
    this_year = get_this_academic_year()
    if grade < 0:
    	years_left = 12 + abs(grade)
    else:
	    years_left = 12 - grade
    return 2000 + this_year + years_left

def string_to_entities(the_string):
	the_string = the_string.replace("\n", '') if the_string else the_string
	if the_string:
		return escape(the_string, html_escape_table)
	return the_string

def entities_to_string(the_string):
	if the_string:
		return unescape(the_string, html_unescape_table)
	return the_string


if __name__ == "__main__":

	print(string_to_entities(u'Hi there–Dude 1/100 ----- ¼'))
	print(get_this_academic_year())
	print(get_year_of_graduation(12))
	print(get_year_of_graduation(-2))