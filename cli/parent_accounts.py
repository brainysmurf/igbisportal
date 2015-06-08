import click
from portal.db import Database, DBSession
db = Database()
Students = db.table_string_to_class('student')
from sqlalchemy.orm import joinedload
from collections import defaultdict

class Family:
    """
    A family built from parent_accounts
    TODO: Make this part of the model more formally?
    """
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

        return "Parents of " + ret

    @property
    def email(self):
        return "family." + self.family_id + "@igbis.edu.my"

    def __init__(self):
        self.students = []
        self.parents = []
        self.family_id = None

class ParentAccounts:
    parent_links = defaultdict(list)
    families = defaultdict(list)

    students = {}
    parents = {}

    family_id_index = 0

    family_accounts = {}

    def __init__(self):
        self.build()

    @classmethod
    def make_family_id(cls):
        ret = str(cls.family_id_index).zfill(4)
        cls.family_id_index += 1
        return ret

    @classmethod
    def make_parent_link(cls, parent, student):
        ParentAccounts.parent_links[parent.id].append(student)

    def build(self):
        """
        Builds self.parents and self.families based on Database.
        Any family is defined as students who share the same parent contact details
        ManageBac guarantees that this is the case.
        """

        # TODO: command-line verbosity
        verbose = False

        with DBSession() as session:
            statement = session.query(Students).options(joinedload('parents')).order_by(Students.student_id)
            for student in statement.all():
                ParentAccounts.students[str(student.id)] = student
                for parent in student.parents:
                    ParentAccounts.parents[parent.id] = parent
                    ParentAccounts.make_parent_link(parent, student)

            for parent_id, students in ParentAccounts.parent_links.items():
                student_ids = "+".join([str(s.id) for s in students])
                ParentAccounts.families[student_ids].append(parent_id)

            self.family_accounts = []
            self.parent_accounts = []

            for key in ParentAccounts.families.keys():
                fam = Family()
                family_id = ParentAccounts.make_family_id() 
                fam.family_id = family_id

                verbose and click.echo(family_id + '_')
                stu_index = 0
                for student_id in key.split('+'):
                    student = ParentAccounts.students[student_id]

                    _sid = "{}{}".format(family_id, stu_index)
                    fam.students.append(student)

                    verbose and click.echo("\t{} ({})".format(student, _sid))
                    stu_index += 1

                    parent_index = 9
                    for parent_id in ParentAccounts.families[key]:
                        parent = ParentAccounts.parents[parent_id]

                        _pid = "{}{}".format(family_id, parent_index)

                        if parent not in fam.parents:
                            fam.parents.append( parent )
                        parent.igbid = _pid

                        verbose and click.echo("\t\t {} ({})".format(parent.igbis_email_address, _pid))
                        parent_index -= 1

                self.family_accounts.append(fam)

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

    def output(self):
        import gns


        for gns.family in self.family_accounts:

            for gns.parent in gns.family.parents:
                click.echo( gns(
                    'gam create user \'{parent.igbis_email_address}\' '\
                    'firstname "{parent.first_name}" '\
                    'lastname "{parent.last_name}" '\
                    'password defaultpassword '\
                    'changepassword on '\
                    'gal off '\
                    'org Parents '\
                    'type {parent.type} '\
                    'externalid IGBID {parent.igbid} '
                ) )

            click.echo( gns(
                'gam create group '\
                '{family.email} '\
                'name "{family.group_name}" '\
                'description "{family.group_name}" '
            ))

            for gns.parent in gns.family.parents:
                click.echo( gns(
                    'gam update group '\
                    '{family.email} '\
                    'add member user \'{parent.igbis_email_address}\''
                ))