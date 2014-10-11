from copy import copy
import weakref

class Container(object):
	students = []
	parents = []
	teachers = []
	classes = []
	groups = []
	ib_groups = []

	def __init__(self):
		self.mapping = {
		'students': self.students, 
		'parents': self.parents,
		'advisors': self.teachers,
		'classes': self.classes,
		'ib_groups': self.groups
		}

	@property
	def users(self):
		l = []
		l.extend(self.students)
		l.extend(self.teachers)
		l.extend(self.parents)
		return l

	@classmethod
	def get_box(cls, which):
		return getattr(cls, which)

	def add(self, dictionary, section):
		dictionary['kindof'] = section.lower()

		class_type = dictionary.get('class_type', '').lower()
		if class_type:
			dictionary['kindof'] = 'classes'
		_type = dictionary.get('type', '')
		if _type:
			dictionary['kindof'] = _type
		mapping = self.mapping.get(dictionary.get('kindof', '').lower(), None)
		if mapping is None:
			print('No type? {}'.format(dictionary))
			from IPython import embed
			embed()
			exit()
			return
		new_one = Abstract.from_dictionary(dictionary)
		mapping.append(new_one)

	def add_reference(self, obj):
		mapping = self.mapping.get(getattr(obj, 'kindof').lower(), None)
		if mapping is None:
			print('No kindof? {}'.format(obj.__dict__))
			return
		mapping.append(weakref.ref(obj))

	@classmethod
	def filter(cls, _type, compare=lambda x, y: x == y, **kwargs):
		"""
		Returns a container instance of the results
		"""
		container = Container()
		box = cls.get_box(_type)
		for thing in box:
			for key in kwargs.keys():
				attr = getattr(thing, key)
				my_attr = kwargs.get(key, None)
				if attr and my_attr and compare(attr, my_attr):
					container.add_reference(thing)
		return container

class Abstract(object):

	def __init__(self, dictionary):
		"""
		Puts every item into here
		"""
		self.__dict__ = copy(dictionary)

	@classmethod
	def from_dictionary(self, info):
		key = info.get('id', None)
		_type = info.get('kindof', None)
		if key is None or _type is None:
			print("No type and/or no id {}".format(info))
		klass = globals().get(_type, None)
		if klass is None:
			return None
		return klass(info)

class Students(Abstract):
	def __init__(self, info):
		super(Students, self).__init__(info)

class Parents(Abstract):
	def __init__(self, info):
		super(Parents, self).__init__(info)

class Advisors(Abstract):
	def __init__(self, info):
		super(Advisors, self).__init__(info)

class Classes(Abstract):
	def __init__(self, info):
		super(Classes, self).__init__(info)

class ib_groups(Abstract):
	def __init__(self, info):
		super(ib_groups, self).__init__(info)
