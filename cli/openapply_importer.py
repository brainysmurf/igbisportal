"""
Read in info from CSV file and update the database appropriately
"""
import csv
from portal.db import Database, DBSession
db = Database()
import click, json, sys
import gns
import requests

Students = db.table_string_to_class('student')
MedInfo = db.table_string_to_class('med_info')

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from portal.db.UpdaterHelper import updater_helper

# Interface to the database
updater = updater_helper.update_or_add

class OA_Medical_Importer:

    def __init__(self, path):
        self.path = path

    @staticmethod
    def translate_headers(x):
        return x.replace(' ', '_').replace('/', '_').replace('-', '')

    @classmethod
    def from_file(cls, path):
        me = cls(path)
        return me

    @classmethod
    def from_api(cls):
        me = cls(None)
        return me

    def read_in_from_file(self):
        with open(self.path, 'rb') as _file:
            reader = csv.reader(_file, dialect='excel')
            headers = reader.next()

            headers = [self.translate_headers(x) for x in headers]

            for row in reader:
                # Get the student info first and then go through the items
                student_id = row[0]
                if not student_id:
                    click.echo("Student info with no student_id? {}".format(":".join(row)))
                    continue
                with DBSession() as session:
                    try:
                        student = session.query(Students).filter_by(student_id=student_id).one()
                    except NoResultFound:
                        student = None
                if not student:
                    click.echo('Student not found {}'.format(student_id))
                    continue

                obj = MedInfo()
                obj.id = student.id

                for i in range(1, len(headers)):
                    header = headers[i]
                    item = row[i]
                    setattr(obj, header, item)

                updater(obj)

    def download_get(self, *args, **kwargs):
        print("Downloading via api: {}".format(args[0]))
        return requests.get(*args, **kwargs)

    def read_in_from_api(self):

        with open(gns('{config.paths.jsons}/open_apply_users.json')) as _f:
            result_json = json.load(_f)

        Students = db.table_string_to_class('student')

        for student in result_json['students']:

            if not student['managebac_student_id']:
                if not student['custom_id']:
                    if student['status'] == 'enrolled':
                        sys.stdout.write(u"Cannot update this student, no custom_id, no managebac_student_id: {}\n".format(student['name']))
                    continue
                with DBSession() as session:
                    try:
                        db_student = session.query(Students).filter(Students.student_id == student['custom_id']).one()
                    except NoResultFound:
                        sys.stdout.write(u"{} not found in database, no student_id: {}\n".format(student['name'], student['custom_id']))
                        continue
                    except MultipleResultsFound:
                        sys.stdout.write(u"Found multiple results when querying {}: {}".format(student['custom_id]'], student['name']))
                        continue
            
                student['managebac_student_id'] = db_student.id
            else:
                #
                # Ensure we actually have a student with this primary Id
                # And that it is right
                # Otherwise we'll end up with an integrity error
                # I am thinking that openapply does NOT play nicely with MB
                #
                if not student['custom_id']:
                    sys.stdout.write(u"Cannot double-check student exists in table! {} no custom_id present!\n".format(student['name']))
                    continue
                with DBSession() as session:
                    try:
                        db_student = session.query(Students).filter(Students.student_id == student['custom_id']).one()
                    except NoResultFound:
                        continue
                    if student['managebac_student_id'] != db_student.id:
                        sys.stdout.write("WORKAROUND for {}".format(student['name']))
                        student['managebac_student_id'] = db_student.id

            # Get the full information
            gns.user_id = student['id']
            url = gns('{config.openapply.url}/api/v1/students/{user_id}')
            this_params = {
                'auth_token': gns.config.openapply.api_token, 
            }

            student_info = self.download_get(url, params=this_params)
            if not student_info.ok:
                print("Download failed")
                continue

            oa_student = student_info.json().get('student')
            oa_student['managebac_student_id'] = student['managebac_student_id']

            health_info = oa_student['custom_fields'].get('health_information')
            vaccination_info = oa_student['custom_fields'].get('immunization_record')
            emerg_contact_info = oa_student['custom_fields'].get('emergency_contact')

            # Construct an instance of MedInfo, building it up
            obj = MedInfo()
            obj.id = oa_student['managebac_student_id']  # This is the managebac primary id, not the student_id (which is a custom field)

            if obj.id:   # might need to investigate how a student ends up with
                #sys.stdout.write("record ID: {}\n".format(obj.id))
                for gns.prefix, info_kind in [('health_information', health_info), ('emergency_contact', emerg_contact_info), ('immunization_record', vaccination_info)]:
                    for index in range(len(info_kind)):
                        gns.index = index + 1

                        # filter out the native id thingie
                        for field in [f for f in info_kind[index].keys() if f != 'id']:
                            gns.field = field
                            this_field = gns('{prefix}_{index}_{field}')
                            # all_columns.add(this_field)
                            #sys.stdout.write(this_field + ': ')

                            value = info_kind[index].get(field)
                            #sys.stdout.write(str(value) + '\n')

                            # Do some value mangling....
                            if isinstance(value, dict):
                                if 'url' in value:
                                    value = value['url']

                            if isinstance(value, list):
                                value = ", ".join(value)
                            setattr(obj, this_field, value)

                # Is there something about a cron context where unicode is different?
                try:
                    print(u"Updating record for {}".format(student['name']))
                except:
                    print("Updating record for {}".format(student['id']))
                updater(obj)
            else:
                sys.stdout.write(u"No managebac_student_id for {}?\n".format(student['name']))

            # print("{}: {}".format(len(list(all_columns)), all_columns))

    def read_in(self):
        if self.path:
            self.read_in_from_file()
        else:
            self.read_in_from_api()

if __name__ == "__main__":
    OA_Importer()