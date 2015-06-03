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
	'>': "&gt;",
	'/': '&frasl;',
	'½': '1&frasl;2',
	'⅓': '1&frasl;3',
	'¼': '1&frasl;4',
}

html_unescape_table = {v:k for k, v in html_escape_table.items()}

from htmlentitydefs import name2codepoint

def string_to_entities(the_string):
	the_string = the_string.replace("\n", '').replace("–", "-") if the_string else the_string
	if the_string:
		return escape(the_string, html_escape_table)
	return the_string

def entities_to_string(the_string):
	if the_string:
		# Don't replace('-', u'\u2013') because not guaranteed
		return unescape(the_string, html_unescape_table)
	return the_string

if __name__ == "__main__":

	print(string_to_entities('Hi there–Dude 1/100 ----- ¼'))