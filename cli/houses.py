
class House(list):
	def __init__(self, num):
		self.num = num

	@property
	def males(self):
		return [s for f in self for s in f.students if s.is_male]

	@property
	def females(self):
		return [s for f in self for s in f.students if s.is_female]

	def like_members(self, student):
		return [f.students[0] for f in self if f.students[0].grade_range == student.grade_range and f.students[0].gender == student.gender]

class Manager(object):

	def __init__(self):
		self.house_index = 0
		self.houses = [House(0),House(1),House(2),House(3)]

	def report_like_members(self, student):
		#print('----')
		#print(student)
		like_members = [len(h.like_members(student)) for h in self.houses]
		m = min(like_members)
		if len([l for l in like_members if l == m]) > 1:
			# more complicated
			lowest_total = min([len(h) for h in self.houses if len(h.like_members(student)) == m])
			potentials = [h for h in self.houses if len(h) == lowest_total]
			if len(potentials) == 1:
				recommendation = potentials[0]
			else:
				# prefer the highest number one
				recommendation = potentials[-1]
		else:
			# simple recommendation
			recommendation = self.houses[like_members.index(m)]
		#for house in self.houses:
		#	pass
			#print('House #{}'.format(house.num))
			#print('{} like members'.format(len(house.like_members(student))))
		#print('Recommend House #{}'.format(recommendation.num))
		return recommendation

	def add_to_house(self, to_add, house=None):
		if isinstance(to_add, list):
			for item in to_add:
				if not house:
					self.houses[self.house_index].append(item)
				else:
					house.append(item)
		else:
			if not house:
				self.houses[self.house_index].append(to_add)
			else:
				house.append(to_add)

	def inc(self):
		self.house_index += 1
		if self.house_index == 4:
			self.house_index = 0

	def report(self):
		i = 1
		for house in self.houses:
			print('House #{}'.format(i))
			print('{} members'.format(len(house)))
			print("{} males".format(len(house.males)))
			print("{} females".format(len(house.females)))
			for r in [1, 10, 100, 1000, 10000]:
				print('{}: {}'.format(
					{1:'lower lower', 10:'lower primary', 100:'upper primary', 1000:'lower seconary', 10000:'higher secondary'}.get(r), 
					len([s for f in house for s in f.students if s.grade_range ==r])))
			print('-----')
			i += 1

		print('-----')
		print('-----')
		print('-----')

		for house in self.houses:
			for family in house:
				for student in family.students:
					print(",".join([family.family_id, student.first_nickname_last_studentid, str(student.grade)]))
			print('-----')

	def best_placement(self, student):
		"""
		The keys
		"""
		pass


from cli.parent_accounts import ParentAccounts

accounts = ParentAccounts()
accounts.family_accounts.sort(key=lambda x: (len(x.students), x.students[0].grade), reverse=True)

fam_index = 0
family = accounts.family_accounts[fam_index]
manager = Manager()

while len(family.students) >= 3:
	manager.add_to_house(family)

	manager.inc()
	fam_index += 1
	family = accounts.family_accounts[fam_index]

#Go through the rest
for family in accounts.family_accounts[fam_index:]:

	house_recommended = manager.report_like_members(family.students[0])
	manager.add_to_house(family, house_recommended)

manager.report()


