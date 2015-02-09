# -*- coding: utf-8 -*-

"""
Utility for converting raw text into html-friendly strings
"""

from xml.sax.saxutils import escape, unescape

html_escape_table = {
	u'“': "&ldquo;",
	u"”": "&rsquo;",
	u"‘": "&lsquo;",
	u"’": "&rsquo;",
	"<": "&lt",
	'>': "&gt;"
}

html_unescape_table = {v:k for k, v in html_escape_table.items()}

def string_to_entities(the_string):
	return escape(example, html_escape_table)

def entities_to_string(the_string):
	return escape(example, html_unescape_table)	