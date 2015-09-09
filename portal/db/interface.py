from portal.db import Database, DBSession
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import gns
import re, json, glob

from portal.db.UpdaterHelper import updater_helper

db = Database()
Student = db.table_string_to_class('Student')
Teacher = db.table_string_to_class('Advisor')
BusAdmin = db.table_string_to_class('BusAdmin')
Parent = db.table_string_to_class('Parent')
Course = db.table_string_to_class('Course')
IBGroup = db.table_string_to_class('IBGroup')

class DatabaseSetterUpper(object):

	def __init__(self, lazy=True, verbose=False):
		self.database = Database()
		#gns.setup_verbosity(self)
		if not lazy:
			self.setup_database()

	def setup_database(self):
		"""
		Reads in file information (made from Go.download) and sets up the database structures
		"""

		#self.default_logger("Setting up additional accounts manually, those who are admins & teachers")

		busadmins = []
		busadmins.append(BusAdmin(first_name="Anne", last_name="Fowles", type="BusAdmin", email="anne.fowles@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="ShuhailaBinti", last_name="MadNasir", type="BusAdmin", email="shuhaila.nasir@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="MDZain", last_name="Mohd", type="BusAdmin", email="md.zain@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Danny", last_name="Yin", type="BusAdmin", email="danny.chan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Mohd", last_name="AbdHalim", type="BusAdmin", email="halim.abdhalim@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Sarah", last_name="Amin", type="BusAdmin", email="sarahain.mohdamin@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Azilahbinti", last_name="RazaliChan", type="BusAdmin", email="azilah.razali@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Mohammad", last_name="Rizal", type="BusAdmin", email="mohdrizal.jali@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Tania", last_name="Nathan", type="BusAdmin", email="tania.nathan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Anderina", last_name="Alexander", type="BusAdmin", email="anderina.alexander@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Stephanie", last_name="LimSuLin", type="BusAdmin", email="stephanie.lim@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Tan", last_name="HueiYin", type="BusAdmin", email="hueiyin.tan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Meena", last_name="Chi", type="BusAdmin", email="meenachi.palanisamy@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Fadlini", last_name="James", type="BusAdmin", email="fadlini.james@igbis.edu.my      "))
		busadmins.append(BusAdmin(first_name="Nazirah", last_name="Saleh", type="BusAdmin", email="nazirah.mohdsaleh@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Noor", last_name="Ismail", type="BusAdmin", email="carolnisak.ismail@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Sarah", last_name="Suhaimin", type="BusAdmin", email="sarah.suhaimin@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Vanessa", last_name="John", type="BusAdmin", email="vanessa.john@igbis.edu.my          "))
		busadmins.append(BusAdmin(first_name="Yvonne", last_name="Peter", type="BusAdmin", email="yvonne.peter@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Lim", last_name="Gigi", type="BusAdmin", email="gigi.lim@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Lim", last_name="Natalie", type="BusAdmin", email="natalie.lim@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Shree", last_name="Narayanasamy", type="BusAdmin", email="devishree.narayanasamy@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Catherine", last_name="DeJonge", type="BusAdmin", email="catherine.dejonge@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Siti", last_name="Khalid", type="BusAdmin", email="siti.khalid@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Rubavathy", last_name="Bojan", type="BusAdmin", email="rubavathy.bojan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Usha", last_name="Krishnan", type="BusAdmin", email="usha.ranikrishnan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Yuly", last_name="Ahmad", type="BusAdmin", email="yuly.ahmad@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Indros", last_name="Roslam", type="BusAdmin", email="indros.roslan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Ahmad", last_name="Aslan", type="BusAdmin", email="shazwan.aslan@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Zulkifli", last_name="Zakaria", type="BusAdmin", email="zulkifli.zakaria@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Choong", last_name="Teresa", type="BusAdmin", email="teresa.choong@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Lee", last_name="ShwuYee", type="BusAdmin", email="shwuyee.lee@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Magenjit", last_name="Singh", type="BusAdmin", email="magenjit.kaur@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Jayaletchumy", last_name="Solan", type="BusAdmin", email="clarissa.jaya@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Thila", last_name="Garani", type="BusAdmin", email="thilagarani.kalimuthu@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Rachel", last_name="Ernhui", type="BusAdmin", email="rachel.kong@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Susie", last_name="Tee", type="BusAdmin", email="susie.tee@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Jegathaswary", last_name="Selveraju", type="BusAdmin", email="jegathaswary.selveraju@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Violet", last_name="Phillip", type="BusAdmin", email="violet.phillip@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Ben", last_name="Voey", type="BusAdmin", email="ben.hor@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Anbalagan", last_name="Subramaniam", type="BusAdmin", email="anbalagan.subramaniam@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Noor", last_name="Abdullah", type="BusAdmin", email="aida.a@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Firdaus", last_name="Sulaiman", type="BusAdmin", email="mohd.firdaus@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Jonathan", last_name="Chong", type="BusAdmin", email="jonathan.chong@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Chris", last_name="Neoh", type="BusAdmin", email="chris.neoh@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Janqi", last_name="Qi", type="BusAdmin", email="janqi.oo@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Nurlina", last_name="Hussin", type="BusAdmin", email="nurlina.hussin@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Harman", last_name="Mazlan", type="BusAdmin", email="harman.harison@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Kalai", last_name="Jagamarthan", type="BusAdmin", email="kalai@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Nor", last_name="Zainudin", type="BusAdmin", email="hamizar.zainudin@igbis.edu.my"))
		busadmins.append(BusAdmin(first_name="Muhammad", last_name="Rusli", type="BusAdmin", email="shah.rusli@igbis.edu.my"))

		admins = []
		admins.append(Teacher(
			id = 10792616,
			first_name= "Adam",
			last_name = "Morris",
			type= "Advisors",
			gender="Male",
			email="adam.morris@igbis.edu.my"
			))

		admins.append(Teacher(
			id = 10792598,
			first_name="Geoffrey",
			last_name ="Derry",
			email="geoffrey.derry@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id=10792614,
			first_name="Matthew",
			last_name="Marshall",
			email="Matthew.Marshall@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id=10792596,
			first_name="Phil",
			last_name="Clark",
			email="Phil.Clark@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10792615,
			first_name="Simon",
			last_name= "Millward",
			email="Simon.Millward@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10754285,
			first_name="Lennox",
			last_name="Meldrum",
			email="lennox.meldrum@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10792603,
			first_name="Peter",
			last_name="Fowles",
			email="peter.fowles@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10792604,
			first_name="Gail",
			last_name="Hall",
			email="gail.hall@igbis.edu.my",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 13546,
			first_name="Super",
			last_name="Admin",
			email="superadmin@managebac.com",
			type="Advisor"
			))

		admins.append(Teacher(
			id = 10958256,
			first_name="Usha",
			last_name ="Ranikrishnan",
			email="usha.ranikrishnan",
			type="Advisor"
			))

		with updater_helper() as u:

			for busadmin in busadmins:
				u.update_or_add(busadmin)

			for admin in admins:
				u.update_or_add(admin)

			for gns.section in gns.config.managebac.sections.split(','):
				#self.default_logger(gns("Setup {section} on database"))

				with open(gns('{config.paths.jsons}/{section}.json')) as _f:
					this_json = json.load(_f)

				_map = dict(Classes="Course", Students="Student", Advisors="Advisor", Parents="Parent")

				for item in this_json[gns.section]:
					_type = item.get('type', None)
					_type = _map.get(_type, _type)
					if not _type:
						if gns.section == 'ib_groups':
							_type = "IB_Group"
						else:
							_type = 'Course' if item.get('class_type') else None
					if not _type:
						print("Object is causing us trouble can't go on without resolving: 'item' doesn't have legit 'type'?")
						exit()

					# Convert any empty string values to None
					item = {k: v if not v == "" else None for k,v in item.items()}

					table_class = self.database.table_string_to_class(_type)
					instance = table_class()
					for item_key in item:
						try:
							# Set up the instance to have the expected values
							setattr(instance, item_key, item[item_key])

						except AttributeError:
							if item[item_key] is None:
								continue  # happens when None is put on there
							else:
								# TODO: Figure this out
								# print?
								# print('here')
								# from IPython import embed
								# embed()
								# exit()
								pass

					# Filter out things
					# Don't go ahead unless a studentid has been given
					# TODO: Shouldn't this really be enforced in the model?
					# 		Maybe check for constaints? 
					if _type == "Student":
						if hasattr(item, 'student_id') and not item['student_id'] is None:
							# TODO: Inform someone?
							print('Student without student_id: {}'.format(item))
							continue

					u.update_or_add(instance)

			with u.collection(Student, Parent, 'parents', left_column='student_id') as stu_par:

				with open(gns('{config.paths.jsons}/users.json')) as _f:
					this_json = json.load(_f)

				#self.default_logger("Setting up student-parent relations on database")
				for user in this_json['users']:
					_type = user.get('type')
					if _type == "Students":
						student_id = user.get('student_id')	
						for parent_id in user.get('parents_ids'):
							stu_par.append(student_id, parent_id)

			with u.collection(Student, IBGroup, 'ib_groups', left_column='student_id') as stu_ibgroup:
				#self.default_logger("Setting up student IB Group membership on database")
				with open(gns('{config.paths.jsons}/ib_groups.json')) as _f:
					this_json = json.load(_f)

				for ib_group in this_json['ib_groups']:
					gns.group_id = ib_group.get('id')
					gns.id = gns.group_id
					gns.uri = gns.config.managebac.ib_groups_section_url.replace('/', '-')

					# Two gns calls because uri has {id} in it
					with open(gns(gns('{config.paths.jsons}/{uri}.json'))) as _f2:
						members_json = json.load(_f2)

					for student_item in members_json['members']:
						gns.student_id = student_item.get('student_id')
						if not gns.student_id:
							continue
						stu_ibgroup.append(gns.student_id, gns.group_id)						

			with u.collection(Teacher, Course, 'classes') as teacher_course:
				#self.default_logger("Setting up teacher class assignments on database")
				with open(gns('{config.paths.jsons}/classes.json')) as _f:
					this_json = json.load(_f)
				for clss in this_json['classes']:
					for teacher in clss.get('teacher'):
						teacher_id = teacher.get('teacher_id')
						course_id = clss.get('id')

						if teacher_id and course_id:
							teacher_course.append(teacher_id, course_id)

			with u.collection(Student, Course, 'classes', left_column='student_id') as stu_course:

				#self.default_logger("Setting up student class enrollments on database")
				for path in glob.glob(gns('{config.paths.jsons}/groups-*-members.json')):
					with open(path) as _f:
						this_json = json.load(_f)

					with DBSession() as session:
						course_id = re.match(gns('{config.paths.jsons}/groups-(\d+)-members.json'), path).group(1)
						for course in this_json['members']:
							student_id = course.get('student_id')
							if student_id is None:
								continue
							try:
								stu_course.append(student_id, course_id)
							except NoResultFound:
								pass
								#print('course_id {} or student_id {} not found'.format(course_id, student_id))

			#self.default_logger("Done!")

if __name__ == "__main__":

	go  = DatabaseSetterUpper(lazy=False)
