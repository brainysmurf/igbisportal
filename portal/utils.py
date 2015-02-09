# -*- coding: utf-8 -*-

"""
Utility for converting raw text into html-friendly strings
"""

from xml.sax.saxutils import escape, unescape

html_escape_table = {
	u'“': "&ldquo;",
	u"”": "&rdquo;",
	u"‘": "&lsquo;",
	u"’": "&rsquo;",
	"<": "&lt;",
	'>': "&gt;"
}

html_unescape_table = {v:k for k, v in html_escape_table.items()}

def string_to_entities(the_string):
	the_string = the_string.replace("\n", '') if the_string else the_string
	if the_string:
		return escape(the_string, html_escape_table)
	return the_string

def entities_to_string(the_string):
	if the_string:
		return unescape(the_string, html_unescape_table)
	return the_string