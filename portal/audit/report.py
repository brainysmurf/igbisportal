import csv, datetime
from dateutil import parser

class Row(object):
	"""
	Object in memory that represents a row in the file
	"""
	columns = []   # represents the columns that are present in the text file

	def __init__(self, **kwargs):
		for kwarg in kwargs:
			key = kwarg.replace(' ', '_').lower()
			setattr(self, key, kwargs[kwarg])

	@classmethod
	def set_columns(cls, columns):
		cls.columns = columns

	@classmethod
	def from_row(cls, row):
		"""
		Create instance based on raw row information
		"""
		d = {}
		for c in range(len(cls.columns)):
			key = cls.columns[c]
			value = row[c]
			d[key] = value

		# Okay, now that we have a dict with the raw information
		# we can make an instance
		return Row(**d)

class Rows(object):
	"""
	Manages all list of row
	"""
	def __init__(self):
		self.rows = []

	def add_row(self, row):
		new_row = Row.from_row(row)
		self.rows.append(new_row)

class Kind(object):
	def __init__(self, raw):
		self.raw = raw

	def __repr__(self):
		return self.raw

	def __str__(self):
		return self.raw

class date(Kind):
	def __init__(self, raw):
		super(self.__class__, self).__init__(raw)
		self.date = parser.parse(raw)

class event_description(Kind):
	def __init__(self, raw):
		super(self.__class__, self).__init__(raw)
		pre, post = raw.split(' changed visibility access level from ')
		self.who = pre
		self.from_, more = post.split(' to ')
		self.to_, self.for_ = more.split(' for ')
		if self.for_ == 'igbis.edu.my' and self.to_ != 'None':
			self.with_link = True
		else:
			self.with_link = False
		if self.for_ == 'all' and self.to_ != 'None':
			self.public = True
		else:
			self.public = False

class Document(object):
	"""
	Represents a document with everything that has happened to it, with most recent on top
	"""
	def __init__(self, document_id):
		self.document_id = document_id

	def add_info(self, **kwargs):
		for key in [k for k in kwargs if k != 'document_id']:
			if not hasattr(self, key):
				setattr(self, key, [])

			klass = globals().get(key)
			if klass:
				obj = klass(kwargs[key])
			else:
				obj = kwargs[key]
			getattr(self, key).append( obj )

	@property
	def sorted_event_descriptions(self):
		# Monkey patch a date object into the event description
		for d in range(len(self.date)):
			date_obj = self.date[d].date
			self.event_description[d].date = date_obj

		# Now we can sort them
		return sorted(self.event_description, key=lambda x: x.date)

	def __repr__(self):
		return "<Document document_id:{} events:{}>".format(self.document_id, "; ".join([str(e) for e in self.event_description]))

class Documents(object):
	"""
	Manages all the events
	"""
	def __init__(self):
		self.documents = {}

	@property
	def touched(self):
		lst = []
		for key in self.documents:
			doc = self.documents[key]
			events = doc.sorted_event_descriptions
			doc.date_sort_by = events[0].date
			lst.append(doc)
		return sorted(lst, key=lambda x: x.date_sort_by, reverse=True)


	def get_document(self, document_id):
		exists = self.documents.get(document_id)
		if not exists:
			d = Document(document_id)
			self.documents[document_id] = d
			return self.documents[document_id]
		return exists


class AuditReport(object):
	"""
	Reads in data from download that reports on any documents where
	Parents or Students can accidentally stumble upon.
	"""

	def __init__(self, path):
		"""
		Read in data
		"""
		self.row_manager = Rows()

		with open(path) as csvfile:
			row_num = 1
			for row in csv.reader(csvfile):
	
				if row_num == 1:
					# We know the first row is a list of columns, so detect that
					# and send it to the Row class, so that when we create the objects
					# it'll all match up
					Row.set_columns(row)
					row_num = 2

				else:
					self.row_manager.add_row(row)
					row_num += 1

		self.collate_and_analyze()

	def collate_and_analyze(self):
		"""
		Takes the raw data and converts it into structures that allows us to filter and view
		"""
		# This is the collation stage
		self.doc_manager = Documents()
		for row in self.row_manager.rows:
			doc = self.doc_manager.get_document(row.document_id)
			doc.add_info(**row.__dict__)

		# This is the analyzation stage
		for doc in self.doc_manager.touched:
			header = False
			for event in doc.sorted_event_descriptions:
				if (event.with_link or event.public) and not header:
					print('----------------------------------')
					print(doc.title[-1])
					print('http://drive.google.com/open?id={}'.format(doc.document_id))
					header = True
				if event.with_link:
					print('Made accessible with link:')
				if event.public:
					print('Made accessible publicly:')
				if event.with_link or event.public:
					print(' Who: {}'.format(event.who))
					print('From: {}'.format(event.from_))
					print('  To: {}'.format(event.to_))
					print('When: {}'.format(event.date.strftime('%b %d %Y')))

report = AuditReport('/Users/adam.morris/Downloads/AuditReport-20150905-2022.csv')
print('finished')
#from IPython import embed;embed()