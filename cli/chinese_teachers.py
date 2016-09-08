# MENU thingie for me to make it easy to maintain chinese teacher lists
#

from portal.db import Database, DBSession
db = Database()
Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')

if __name__ == "__main__":

