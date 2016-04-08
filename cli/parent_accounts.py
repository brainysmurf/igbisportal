import click
from portal.db import Database, DBSession
db = Database()
Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from collections import defaultdict
from sqlalchemy import and_
import gns
import datetime

"""
ManageBac doesn't export the grade information, just the homeroom advisor,
So this provides a workaround
"""
homeroom_mapping = {
    'rachel.fleury':(6, '6'),
    'tim.bartle': (7, '7'),
    'sheena.kelly': (7, '7'), 
    'benjamin.wylie': (8, '8'),
    'emily.heys': (8, '8'),
    'dean.watters':(9, '9'),
    'glen.fleury': (9, '9'),
    'marcus.wetherell': (10, '10'),
    'diane.douglas': (10, '10'),
    'paul.skadsen': (11, '11'),
    'nathalie.chotard': (11, '11'),
    'gabriel.evans': (11, '11'),
    'michael.hawkes': (12, '12'),
    'mary.richards': (-9, 'EY{}R'),
    'deborah.king': (-9, 'EY{}K'),
    'sally.watters': (-9, 'EY{}W'),
    'leanne.harvey':(0, 'KH'),
    'lisa.mcclurg': (0, 'KM'),
    'shireen.blakeway': (1, '1B'),
    'kath.kummerow': (2, '2K'),
    'michelle.ostiguy': (3, '3O'),
    'marshall.hudson': (3, '3H'),
    'kari.twedt': (4, '4T'),
    'steven.harvey': (4, '4H'),
    'kathy.mckenzie': (5, '5M'),
    'yolaine.johanson': (5, '5J'),
    }

class Error(Exception):
    def __str__(self):
        return self.msg

class NotFoundError(Error):
    pass

class NoHomeroomTeacherFound(NotFoundError):
    def __init__(self, msg=""):
        self.msg = msg

class Family:
    """
    A family built from parent_accounts
    TODO: Make this part of the model more formally?
    """

    def __repr__(self):
        return "<#: {}, {}>".format(len(self.students), self.students[0].grade)

    @property
    def group_name(self):
        ret = "Parents of "

        # if they have the same last name
        if len(set([s.last_name for s in self.students])) == 1:
            first = " & ".join([s.first_nickname for s in self.students])
            last = self.students[0].last_name
            ret = first + ' ' + last
        # or they have different last names
        else:
            ret = " & ".join([s.first_nickname_last for s in self.students])

        return "Parents of {}".format(ret)

    @property
    def email(self):
        return "family." + self.family_id + "@igbis.edu.my"

    def __init__(self):
        self.students = []
        self.parents = []
        self.family_id = None

class ParentAccounts:
    """
    Holds the data for building up the account information
    """
    parent_links = defaultdict(list)    # data construct: a hash with each item an array
    families = defaultdict(list)        # data construct: a hash with each item an array
    groups = {}

    students = {}                       # hash of all the students
    parents = {}                        # hash of all the parents
    classes = {}

    family_id_index = 0

    family_accounts = {}                # hash of all the family accounts 

    def __init__(self, since=None):
        self._since = since
        self._tomorrow = datetime.datetime.now().date() + datetime.timedelta(days=1)
        self.build()

    @classmethod
    def make_family_id(cls):
        ret = str(cls.family_id_index).zfill(4)
        cls.family_id_index += 1
        return ret

    @classmethod
    def make_parent_link(cls, parent, student):
        ParentAccounts.parent_links[parent.id].append(student)

    def make_parent_group(self, group, email=None):
        ParentAccounts.groups[group] = type('Parents Group', (), {})
        ParentAccounts.groups[group].name = "Parents of " + group
        ParentAccounts.groups[group].email = group if email is None else email
        ParentAccounts.groups[group].email += '.parents@igbis.edu.my'
        ParentAccounts.groups[group].list = []

    def make_class_group(self, group, email=None):
        if not group in ParentAccounts.classes:
            ParentAccounts.classes[group] = type("Parents Classes Group", (), {})
            ParentAccounts.classes[group].name = "Parents of children enrolled in classs " + group
            ParentAccounts.classes[group].email = group if email is None else email
            ParentAccounts.classes[group].list = []

    def build_query(self, session):
        if not self._since:
            return session.query(Students).options(joinedload('parents'),joinedload('classes')).\
                filter(
                        Students.is_archived==False
                    ).order_by(Students.student_id)
        else:
            # TODO: attendance_start_date REALLY needs to be a freaking date column
            return session.query(Students).options(joinedload('parents'),joinedload('parents')).\
                filter(and_(
                    Students.is_archived==False,
                    func.to_timestamp(func.coalesce(Students.attendance_start_date, '3000-01-01'), "YYYY-MM-DD") >= self._since, 
                    func.to_timestamp(func.coalesce(Students.attendance_start_date, '3000-01-01'), "YYYY-MM-DD") <= self._tomorrow
                    )
                ).order_by(Students.student_id)

    def build(self):
        """
        Builds self.parents and self.families based on Database.
        Any family is defined as students who share the same parent contact details
        ManageBac guarantees that this is the case.
        """

        # TODO: command-line verbosity
        verbose = False
        gns.suffix = '.parent'
        gns.domain = '@igbis.edu.my'


        # First do the groups

        for group in ['Secondary', 'Elementary', 'Whole School', 'Grade 12', 'Grade 11', "Grade 10", "Grade 9", "Grade 8", "Grade 7", "Grade 6", "Grade 5", "Grade 4", "Grade 3", "Grade 2", "Grade 1", "Kindergarten", "Early Years 1", "Early Years 2", "Fireflies"]:
            self.make_parent_group(group, group.lower().replace(' ', ''))

        for username, _ in homeroom_mapping.items():
            grade, homeroom = _
            if grade >= 6:
                group = 'homeroom.' + homeroom + (username.split('.')[1][0]).lower()
            elif grade >= -2:
                group = 'homeroom.' + homeroom
            elif grade == -9:
                for i in [1, 2]:
                    self.make_parent_group('homeroom.'+ homeroom.format(i))

            if grade >= -2:
                self.make_parent_group(group)

        with DBSession() as session: # this opens a connection to the database

            # Emit SQL to get all all the students, and join with parent information
            statement = self.build_query(session)
            students = statement.all()

            # loop through each student, which has parent info and other model information
            # in the end we'll have a data construct with parent links
            for student in students:
                # save the student information, we'll grab this later
                ParentAccounts.students[str(student.id)] = student

                if student.grade != -10:
                    # Filter out students who do not have a grade assigned.
                    # ... those are probably students that are enrolled in a grade but don't have a homeroom assigned
                    # ... sometimes happens, could be an error?
                    try:
                        teacher = session.query(Teachers).filter(Teachers.id==student.homeroom_advisor).one()
                    except NoResultFound:
                        teacher = None
                        NoHomeroomTeacherFound(msg='{} student has {} for homeroom teacher id but cannot find in table'.format(student, student.homeroom_advisor))

                    if teacher:
                        grade, homeroom = homeroom_mapping.get(teacher.username_handle, (None, None))
                        if grade is None or homeroom is None:
                            print('grade is None or homeroom is None')
                            continue

                        if grade >= 6:
                            homeroom_level_group = 'homeroom.' + homeroom + (teacher.username_handle.split('.')[1][0]).lower()
                        elif grade >= -2:
                            homeroom_level_group = 'homeroom.' + homeroom
                        elif grade == -9:
                            for i in [1, 2]:
                                homeroom_level_group = 'homeroom.' + homeroom.format(i)
                                for parent in student.parents:
                                    ParentAccounts.groups[homeroom_level_group].list.append(parent.igbis_email_address)

                        if grade >= -2:
                            try:
                                for parent in student.parents:
                                    ParentAccounts.groups[homeroom_level_group].list.append(parent.igbis_email_address)
                            except KeyError:
                                print("Key Error: {}".format(homeroom_level_group))
                                #from IPython import embed;embed()

                for class_ in student.classes:
                    if class_.uniq_id:
                        self.make_class_group(class_.uniq_id)
                        for parent in student.parents:
                            ParentAccounts.classes[class_.uniq_id].list.append(parent.email)

                for parent in student.parents:
                    # Add the more global ones whole school and school-based ones


                    # save the parent inforamtion, we'll grab this later
                    ParentAccounts.parents[parent.id] = parent

                    # Add this student onto the array stored where parent.id is the key
                    # Guaranteed to work because the parent info are just links to the same database entry
                    # So even if they change their name, or anything, still all good
                    ParentAccounts.make_parent_link(parent, student)

                    if student.class_grade is not None:
                        ParentAccounts.groups[student.class_grade].list.append(parent.igbis_email_address)
                        ParentAccounts.groups['Whole School'].list.append(parent.igbis_email_address)
                        if student.grade is not None:
                            if student.grade >= 6:
                                ParentAccounts.groups['Secondary'].list.append(parent.igbis_email_address)
                            else:
                                ParentAccounts.groups['Elementary'].list.append(parent.igbis_email_address)

                    else:
                        print("Student without a grade level {}".format(student))

            #from IPython import embed;embed();exit()

            # loop through each of the parent links, making a new data construct (families)
            # this time the keys is the student ids as a string concated, with "+"" as delimiter
            # we'll unpack this later
            for parent_id, students in ParentAccounts.parent_links.items():
                student_ids = "+".join([str(s.id) for s in students])
                ParentAccounts.families[student_ids].append(parent_id)


            # at this point we have families with the key being a concat of the student ids
            # that maps to an array of parents
            # initialize:
            self.family_accounts = []
            self.parent_accounts = []

            # loop through the family information
            for key in ParentAccounts.families.keys():
                fam = Family()   # makes a new object. TODO: this should be a table in the database
                family_id = ParentAccounts.make_family_id() 

                # derive family_id, and save it in the object
                fam.family_id = family_id

                verbose and click.echo(family_id + '_')

                stu_index = 0  # first child is 0, counting up

                # FIXME: Check for _sid and _pid collisions

                for student_id in key.split('+'):                  # loop through each student ID contained in this key
                    student = ParentAccounts.students[student_id]  # grab the student that we saved before
                    _sid = "{}{}".format(family_id, stu_index)     # derive the student igbid

                    fam.students.append(student)                    # append student info to the family object

                    verbose and click.echo("\t{} ({})".format(student, _sid))
                    stu_index += 1

                    parent_index = 9   # first parent is 9, counting down
                    for parent_id in ParentAccounts.families[key]:
                        parent = ParentAccounts.parents[parent_id]

                        # derive the parent igbid, which we'll set
                        # second line actually emits update sql
                        _pid = "{}{}".format(family_id, parent_index)
                        parent.igbid = _pid

                        # now append the parent, but not if already in there
                        if parent not in fam.parents:
                            fam.parents.append( parent )

                        verbose and click.echo("\t\t {} ({})".format(parent.igbis_email_address, _pid))
                        parent_index -= 1

                self.family_accounts.append(fam)

        # print('here')
        #from IPython import embed;embed()
        # end of with statement:
        # SQL is emitted here, and database connection closes

    def output(self):
        for parent in self.parent_accounts:
            click.echo(parent)

        for family in self.family_accounts:
            click.echo(family.group_name)

    def output_family(self):

        with DBSession() as session:

            statement = session.query(Students).options(joinedload('parents')).order_by(Students.student_id)
            for student in statement.all():
                for parent in student.parents:
                    click.echo("\t{} {}".format(ParentAccounts.make_family_id(student, parent), parent))

    def output_for_email(self):

        click.echo( gns(
                'Parent First Name'\
                '{COMMA}'\
                'Parent Last Name'\
                '{COMMA}'\
                'Children'\
                '{COMMA}'\
                'Parent Registered Email'
                '{COMMA}'\
                'Parent IGBIS Email'
            ))

        for gns.family in self.family_accounts:

            for gns.parent in gns.family.parents:
                gns.children = " and ".join([s.first_nickname_last_studentid for s in gns.family.students])
                click.echo( gns(
                    '{parent.first_name}'\
                    '{COMMA}'\
                    '{parent.last_name}'\
                    '{COMMA}'\
                    '{children}'
                    '{COMMA}'\
                    '{parent.email}'\
                    '{COMMA}'\
                    '{parent.igbis_email_address}'\
                    '{COMMA}'\
                ))

    def output(self):

        for group in ParentAccounts.groups:
            gns.group = ParentAccounts.groups[group]
            click.echo( gns(
                    'gam create group \'{group.email}\' '\
                    'name \'{group.name}\''\
                ))

        click.echo('commit-batch')

        for gns.family in self.family_accounts:

            for gns.parent in gns.family.parents:
                click.echo( gns(
                    'gam create user \'{parent.igbis_email_address}\' '\
                    'firstname "{parent.first_name}" '\
                    'lastname "{parent.last_name}" '\
                    'password \'igbis\' '\
                    'changepassword on '\
                    'gal off '\
                    'org Parents '\
                    'externalid IGBID {parent.igbid} '
                ))

                # Need to route this to subprocess
                # click.echo( gns(
                #     'gam info user \'{parent.igbis_email_address}\' '\
                #     'nogroups noaliases nolicenses noschemas '
                # ))

            # click.echo( gns(
            #     'gam create group '\
            #     '\'{family.email}\' '\
            #     'name "{family.group_name}" '\
            #     'description "{family.group_name}" '
            # ))

            # for gns.parent in gns.family.parents:
            #     click.echo( gns(
            #         'gam update group '\
            #         '\'{family.email}\' '\
            #         'add member user \'{parent.igbis_email_address}\''
            #     ))


        click.echo('commit-batch')

        for group in ParentAccounts.groups:
            gns.group = ParentAccounts.groups[group]            
            for gns.parent_email in gns.group.list:
                click.echo( gns(
                    'gam update group '\
                    '\'{group.email}\' '\
                    'add member user \'{parent_email}\''
                    )
                )

        for class_ in ParentAccounts.classes:
            gns.group = ParentAccounts.classes[class_]
            for gns.parent_email in gns.group.list:
                click.echo( gns(
                    'gam update group '
                    '\'{group.email}\' '
                    'add member user \'{parent_email}\''
                    )
                )


