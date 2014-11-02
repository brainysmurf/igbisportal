# -*- coding: utf-8 -*-

"""
Defines a scrapy.item that keeps the order defined in the source code and handles python dates
Intended to be used to make a JSON
Dates will work as long as they have an isoformat method, as does a datetime.datetime object

Motivation:
For apps that want a JSON of data in a particular order rather than by named keys, we want our scraper stuff
to know about this order natively in the source code, but the provided scraper.item stuff uses just a regular dict,
so we override the necessary behavoiur to use an OrderedDict instead.

Originally written when trying to send json data over to JQuery's datatables.
"""

import scrapy
from collections import OrderedDict
import six
import json

class OrderedDictForJSONItem(scrapy.item.DictItem):

    # class Encoder(json.JSONEncoder):
    #     """
    #     This gets called when python runs into the data object, or something else it doesn't know about
    #     """
    #     def default(self, obj):
    #         if hasattr(obj, 'isoformat'):
    #             return obj.isoformat()
    #         else:
    #             return json.JSONEncoder.default(self, obj)

    @property
    def tojson(self):
        values = self._values.values()
        return json.dumps(values)

    def __init__(self, *args, **kwargs):
        self._values = OrderedDict()
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in six.iteritems(dict(*args, **kwargs)):
                self[k] = v

    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value
        else:
            raise KeyError("%s does not support field: %s" %
                (self.__class__.__name__, key))

	def __setattr__(self, name, value):
		if not name.startswith('_'):
			raise AttributeError("Use item[%r] = %r to set field value" %
				(name, value))
		super(OrderedDictItem, self).__setattr__(name, value)

    def __repr__(self):
        return repr(self._values.values())

@six.add_metaclass(scrapy.item.ItemMeta)
class OrderedItem(OrderedDictForJSONItem):
	pass


