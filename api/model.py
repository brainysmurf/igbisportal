from copy import copy
import weakref

class Container(object):
	students = []
	parents = []
	teachers = []

	def __init__(self):
		self.mapping = {
		'students': self.students, 
		'parents': self.parents,
		'advisors': self.teachers
		}

	@classmethod
	def get_box(cls, which):
		return cls.mapping.get(which)

	def add(self, dictionary):
		mapping = self.mapping.get(dictionary.get('type', None).lower(), None)
		if mapping is None:
			print('No type? {}'.format(dictionary))
		mapping.append(Abstract.from_dictionary(dictionary))

	def add_reference(self, obj):
		mapping = self.mapping.get(dictionary.get('type', None).lower(), None)
		if mapping is None:
			print('No type? {}'.format(dictionary))
		mapping.append(weakref.ref(obj))

	@classmethod
	def filter(cls, _type, compare=lambda x, y: x == y, **kwargs):
		"""
		Returns a container instance of the results
		"""
		container = Container()
		box = cls.get_box(_type)
		for student in box:
			for key in kwargs.keys():
				attr = getattr(student, key)
				my_attr = kwargs.get(key, None)
				if attr and my_attr and compare(attr, my_attr):
					container.add_reference(student)
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
		_type = info.get('type', None)
		if key is None or _type is None:
			print("No type and/or no id {}".format(info))
		klass = globals().get(_type, None)
		if klass is None:
			return None
		return klass(info)

class Students(Abstract):
	def __init__(self, info):
		super(Students, self).__init__(info)
		print('Student: {}'.format(info))

class Parents(Abstract):
	def __init__(self, info):
		super(Parents, self).__init__(info)
		print('Parent: {}'.format(info))

