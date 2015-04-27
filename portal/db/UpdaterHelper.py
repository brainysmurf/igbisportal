from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
from collections import defaultdict

# Makes an object so we can use dot notation
DO = lambda name, **kwargs: type(name, (), kwargs)

class collection_obj:
	def __init__(self, left_table, right_table, collection, left_column='id', right_column='id'):
		"""
		Initialize the table information

		@param left, right:  SQLALchemy table
		@param collection: name of SQLAlchemy collection
		"""
		self._collection_list = defaultdict(list)
		self.left_table = left_table
		self.right_table = right_table
		self.left_column = left_column
		self.right_column = right_column
		self.collection = collection

	def _parse_table_info(self, left_id, right_id):
			
		left_by = {self.left_column: left_id}
		right_by = {self.right_column: right_id}

		# return an object that defines the information
		return DO('Table Info', 
			left=DO(
				self.left_table.__name__,
				table=self.left_table,
				by=left_by
				),
			right=DO(
				self.right_table.__name__,
				table=self.right_table,
				by=right_by
			))
		#return dict(left=dict(id=left_id, by=left_by), right=dict(id=right_id, by=right_by))

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		pass   # Don't do anything

	def append(self, left, right):
		"""
		Append to the collection if not present, or, if already present, do nothing
		@param left,right: if object then should be {id_name, id}, otherwise int and looked up via 'id'
		TODO: Shift this definition to the __init__ call?
		"""

		with DBSession() as session:

			ti = self._parse_table_info(left, right)

			left_row = session.query(ti.left.table).filter_by(**ti.left.by).one()
			right_row = session.query(ti.right.table).filter_by(**ti.right.by).one()

			# Keeps a record of everything that has been appended
			# TODO: Inspect to see what is used as the foreign key, assuming .id
			if right_row.id not in self._collection_list[left_row.id]:
				self._collection_list[left_row.id].append(right_row.id)

			if right_row.id in [item.id for item in getattr(left_row, self.collection)]:
				return # already there, don't do anything
			else:
				# This actually emits the sql:
				getattr(left_row, self.collection).append(right_row)
				print("Added {} to {} into {} collection".format(right_row.id, left_row.id, self.collection))

class updater_helper:
	def __init__(self):
		self._collections = {}

	def __enter__(self):
		self.left_table_ids= []
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if not all([exc_type, exc_value, traceback]):
			# automatically see if there are any to be deleted
			for key in self._collections.keys():
				collection = self._collections[key]

				for left_id in collection._collection_list.keys():
					ids_appended = collection._collection_list[left_id]

					with DBSession() as session:
						# Find by id, TODO: Change this to using primary key(s)
						left_row = session.query(collection.left_table).filter_by(id=left_id).one()
						ids_on_db = [item.id for item in getattr(left_row, collection.collection)]

						# Look for items that are in ids_on_db but not in ids_appended, because that means we should delete them
						for id_to_delete in set(ids_on_db) - set(ids_appended):
							right_row = session.query(collection.right_table).filter_by(id=id_to_delete).one()
							print('removed {} from {} in collection {}'.format(right_row.id, left_row.id, collection.collection))
							getattr(left_row, collection.collection).remove(right_row)

	def update_or_add(self, obj):
		"""
		@param obj: An SQLAlechemy table instance

		Look at the table information provided by obj
		If it's not there, add it
		If it there, update anything that is different
		"""
		with DBSession() as session:
			try:
				row = session.query(obj.__class__).filter_by(id=obj.id).one()
			except NoResultFound:
				session.add(obj)
				print('Added new {}'.format(obj))
				return

			if row:
				column_names = [c.name for c in row.__table__.columns if c.name != 'id']
				for column in column_names:
					left = getattr(row, column)  # has
					right = getattr(obj, column) # needs

					# If there are some values that are different, construct an update object
					# and execute with the session obj
					if right and left != right:
						values_statement = {column: right}
						update_obj = obj.__table__.update().\
							where(obj.__table__.c.id == obj.id).\
							values(**values_statement)
						session.execute(update_obj)
						print('{} updated {} column of table {} change from {} to {}'.format(obj, column, row.__table__, left, right))

	def collection(self, left, right, attr, left_column='id', right_column='id'):
		"""
		Returns class that can be used in with statement
		Keeps record of objects
		"""
		key = left.__name__ + ' + ' + right.__name__
		if key in self._collections:
			return self._collections[key]
		self._collections[key] = collection_obj(left, right, attr, left_column=left_column, right_column=right_column)
		return self._collections[key]


