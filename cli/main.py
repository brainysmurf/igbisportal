import click
import gns
import os
import datetime
import requests
import json
import re
import csv
from PIL import Image
from portal.db import Database, DBSession


class Object(object):
    def __init__(self):
        # chance to get setings
        pass

    # define common methods here


@click.group()
@click.option('--tutorial/--notutorial', default=False, help="Enable step-by-step explanations")
@click.pass_context
def main(ctx, tutorial):
    # Doesn't do much now, but leave it as boilerplate for when there are global flags n such
    ctx.obj = Object()
    if tutorial:
        gns.set_debug(True)


def dl():
    from portal.db.api.interface import AsyncAPIDownloader
    go = AsyncAPIDownloader()
    go.download()


def db_setup(fake=False):
    from portal.db.interface import DatabaseSetterUpper
    go = DatabaseSetterUpper()
    go.setup_database(fake)


@main.group()
def sync():
    """
    Commands that launches syncing with MB and OA
    """
    pass


@sync.command("destiny")
@click.option("--dontput", is_flag=True, default=False, help="Turn off the putting to the file, for debugging")
@click.pass_obj
def destiny(obj, dontput):
    """
    Writes to a location on the server
    Internal use only
    """
    import gns
    secret = gns.config.api.secret
    # field_districtID={1,omit}
    # field_siteShortName={2,omit}
    # field_barcode={3,omit}
    # field_lastName={4,omit}
    # field_firstName={5,omit}
    # field_nickname={6,omit}
    # field_patronType={7,omit}
    # field_homeroom={8,omit}
    # field_gradeLevel={9,omit}
    # field_graduationYear={10,omit}
    # field_gender={11,omit}
    # field_username={12,omit}
    # field_emailPrimary={13,omit}

    payload = {
        'secret': secret,
        'columns': [
            'student_id',
            'destiny_site_information',
            'barcode',
            'last_name',
            'first_name',
            'nickname',
            'destiny_patron_type',
            'homeroom_abbrev_destiny',
            'abbrev_grade_destiny',
            'year_of_graduation',
            'gender_abbrev',
            'username',
            'email',
        ],
    }
    result = requests.get('http://0.0.0.0:6543/api/students', json=payload)
    if result.ok:
        json = result.json()
        data = json.get('data')
        if not data:
            print("BAD")
            return

        path_to_output = gns.config.paths.portal_home + '/output/destinysync.csv'
        # encoding = 'cp1252'    # 'utf-8' or 'cp-1252'
        with open(path_to_output, 'w') as _f:
            for line in data:
                for i in range(len(line)):
                    l = line[i]
                    if i == 0 or i == len(line):
                        pass  # don't write a comma
                    else:
                        _f.write(',')
                    _f.write(str(l))
                _f.write('\r\n')
        import pysftp

        path = gns.config.destiny.path
        host = gns.config.destiny.host
        username = gns.config.destiny.username
        password = gns.config.destiny.password
        if dontput:
            return
        with pysftp.Connection(host, username=username, password=password) as conn:
            with conn.cd(path):
                result = conn.put(path_to_output)
    else:
        print(result.status_code)

@sync.command()
@click.option('--download/--dontdownload', default=True, help='default is --download')
@click.option('--setupdb/--dontsetupdb', default=True, help='default is --setupdb')
@click.option('--fake', is_flag=True, default=False, help='Replace downloaded with fake names')
@click.pass_obj
def managebac(obj, download, setupdb, fake):
    """
    Downloads data from ManageBac APIs, and updates database
    """
    if download:
        dl()
    if setupdb:
        db_setup(fake)

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

@sync.command()
@click.pass_obj
def new_students(obj):
    import gns
    mb_file = gns.config.paths.jsons + '/users.json'
    mb_data = None
    oa_file = gns.config.paths.jsons + '/open_apply_users.json'
    oa_data = None
    import requests, json

    with open(mb_file, 'r') as _f:
        mb_data = json.load(_f)

    with open(oa_file, 'r') as _f:
        oa_data = json.load(_f)

    oa_enrolled_students = {}
    oa_unenrolled_students = {}
    for student in oa_data['students']:
        if 'custom_id' in student:
            if student['status'] == 'enrolled':
                oa_enrolled_students[student['custom_id']] = student
            else:
                oa_unenrolled_students[student['custom_id']] = student

    mb_students = {}
    for student in mb_data['users']:
        if student['type'] == 'Students':
            mb_students[student['student_id']] = student

    to_enroll = []
    for id_, student in oa_enrolled_students.items():
        to_enroll.append(student)

        # if not id_ in mb_students:
        #     name = student['first_name'] + ' ' + student['last_name'] + ' ' + student['grade']
        #     print(u"Found one to enrolled: {}".format(name))
        #     if student['first_name'] not in ['Riko']:
        #         to_enroll.append(student)

    new_user_url = gns.config.managebac.api_url + '/users'
    auth_token = gns.config.managebac.api_token
    for student in to_enroll:
        if student['last_name'] == 'Arcidiacono':
            student['student_id'] = student["custom_id"]
            student['type'] = "student"
            student['year_class'] = student['grade']
            del student['tags']
            del student['status']
            student['welcome_email'] = "Yes"
            data = {'user': student}
            print("POST: {}\npayload:\n{}".format(new_user_url, json.dumps(data, indent=2)))
            # result = requests.post(new_user_url, params={'auth_token':auth_token}, json=data)
            # print(result.status_code)
            # from IPython import embed;embed()
            # assert result.status_code == 201


    #from IPython import embed;embed()

@sync.command()
@click.option('--download/--dontdownload', default=True, help='default is --download')
@click.option('--update/--dontupdate', default=True, help='default is --update')
@click.pass_obj
def update_users(obj, download, update):
    from portal.db.api.interface import APIDownloader
    dload = APIDownloader()

    if download:
        dload.download_all()

    path = dload.build_json_path('users', '.json')
    with open(path, 'r') as _f:
        mb_data = json.load(_f)
    path = dload.build_json_path('open_apply_users', '.json')
    with open(path, 'r') as _f:
        oa_data = json.load(_f)

    # Go through Managebac data
    students = [s for s in oa_data['students'] if s['last_name'].startswith('Arc')]
    api_token = gns.config.managebac.api_token

    for student in students:

        print(student)
        mb_student = [s for s in mb_data['users'] if s.get('student_id') == student['custom_id']][0]
        print(mb_student)
        put_url = gns.config.managebac.api_url + '/users/{}'.format(mb_student['id'])
        if update:
            r = requests.put(put_url, params=dict(
                auth_token=api_token
            ), json={
                'user':
                    {
                        'parents_ids': student['parent_ids']
                    }
            }
            )
        from IPython import embed;embed()


@sync.command()
@click.pass_obj
def photos(obj):
    """
    Get all the student photos you can and download them
    """
    import shutil
    db = Database()

    rootpath = '/home/vagrant/igbisportal/'
    try:
        os.mkdir(rootpath + 'student_photos/')
    except OSError:
        pass
    rootpath = rootpath + 'student_photos/'
    paths = {'sec': rootpath + 'sec/', 'elem': rootpath + 'elem/'}

    for pth in ['sec', 'elem']:
        p = paths.get(pth)
        try:
            os.mkdir(p)
        except OSError:
            shutil.rmtree(p)
            os.mkdir(p)
        if os.path.isfile(p +'idlink.txt'):
            os.remove(p + 'idlink.txt')

    Students = db.table_string_to_class('student')

    # We have to do a get here due to expiries
    # TODO: Make the downloader more robust to allow us to piggyback
    prefix = gns.config.managebac.prefix
    api_url = 'https://{prefix}.managebac.com/api/{uri}'.format(prefix=prefix, uri="users")
    api_token = gns.config.managebac.api_token

    import requests
    print("Downloading via api: {}".format(api_url))
    result = requests.get(api_url, params=dict(
        auth_token=api_token
    ))
    photo_links = dict()
    if not result.ok:
        print("Could not get updated links, attempting to proceed")
    else:
        print('Parsing the data...')
        for user in result.json()['users']:
            if 'student_id' in user and 'profile_photo' in user:
                print("Photo url for student id {} found".format(user['student_id']))
                photo_links[user['student_id']] = user['profile_photo']

    with DBSession() as session:

        students = session.query(Students).filter(Students.status=='enrolled').all()

        for student in students:

            school = 'elem' if student.grade <= 5 else 'sec'
            path = paths.get(school)

            url = student.profile_photo
            if not url:
                continue
            expires = float(re.findall('&Expires=([0-9]+)', url)[0])
            expiry_date = datetime.datetime.fromtimestamp(expires)
            now = datetime.datetime.now()
            if now > expiry_date:   # expired, use downloaded one
                url = photo_links[student.student_id]

            if url is None:
                print("No photo available for {} ... must not be on ManageBac yet".format(student.grade_last_first_nickname_studentid))
                continue

            print(u"Downloading photo for {} to {}".format(student.grade_last_first_nickname_studentid, path))
            r = requests.get(url)
            if r.ok:
                file_name = str(student.student_id)

                with open(path + file_name, 'wb') as _f:
                    _f.write(r.content)

                i = Image.open(path + file_name)
                i.thumbnail((300,300), Image.ANTIALIAS)
                ext = i.format.lower()

                final_name = path + file_name + '.' + ext
                i.save(final_name)

                # Now that saved it, remove the old one
                os.remove(path + file_name)

                with open(path + 'idlink.txt', 'a') as _f:
                    _f.write("{},{}\n".format(student.barcode, file_name + '.' + ext))

    for pth in ['sec', 'elem']:
        p = paths.get(pth)
        shutil.make_archive(p, 'zip', p)

@main.group()
def output():
    """
    Commands that displays information for reference
    """
    pass

@output.command()
@click.pass_obj
def family_info(obj):
    from cli.parent_accounts import ParentAccounts
    parent = ParentAccounts()
    click.echo('-----')
    for family in parent.family_accounts:
        for student in family.students:
            click.echo('{}\t{}'.format(student.email, family.family_id))
        for parent in family.parents:
            click.echo('{}\t{}'.format(parent.igbis_email_address, family.family_id))
    from IPython import embed;embed()

@output.command()
@click.pass_obj
def stats(obj):
    """ Output student/family info """
    from cli.parent_accounts import ParentAccounts
    parent = ParentAccounts()
    family_count = 0
    student_count = 0
    secondary_student_count = 0
    elementary_student_count = 0
    for family in parent.family_accounts:
        family_count += 1
        for student in family.students:
            student_count += 1
            if student.grade >= 6:
                secondary_student_count += 1
            elif student.grade <= 5:
                elementary_student_count += 1

    click.echo("{:<35}: {}".format(click.style("Family Count", fg="green"), family_count))
    click.echo("{:<35}: {}".format(click.style("Student Count", fg="green"), student_count))
    click.echo("{:<35}: {}".format(click.style("Secondary Student Count", fg="green") , secondary_student_count))
    click.echo("{:<35}: {}".format(click.style("Elementary Student Count", fg="green"), elementary_student_count))

@output.command()
@click.pass_obj
def student_columns(obj):
    db = Database()
    Students = db.table_string_to_class('student')
    from IPython import embed;embed()
    click.echo(Students.columns)

@output.command()
@click.pass_obj
def who_does_not_have_parents(obj):
    import json
    from cli.parent_accounts import ParentAccounts
    results = []
    users = gns('{config.paths.jsons}/users.json')
    user_json = None
    with open(users) as f:
        raw = f.read()
        user_json = json.loads(raw)
    for user in user_json['users']:
        if user['type'] == 'Students' and not user.get('parents_ids'):
            print(user['email'])
            results.append(user)
    print(len(results))

@output.command()
@click.option('--since', default=None, help="today for 'today'")
@click.pass_obj
def parent_accounts(obj, since):
    from cli.parent_accounts import ParentAccounts
    if since=='today':
        since = datetime.datetime.now().date()
        parent_accounts = ParentAccounts(since=since)
    elif since:
        how_many = int(re.sub('[^0-9]', '', since))
        since = (datetime.datetime.now() - datetime.timedelta(days=how_many)).date()
        parent_accounts = ParentAccounts(since=since)
    else:
        parent_accounts = ParentAccounts()

    parent_accounts.output()

@output.command()
@click.pass_obj
def contact_information(obj):
    """
    Spits out what is needed for geoff to contact the parents
    """
    from cli.parent_accounts import ParentAccounts
    parent_accounts = ParentAccounts()
    parent_accounts.output_for_email()

@sync.command()
@click.option('path', '--path', type=click.Path(exists=True))
@click.pass_obj
def openapply_from_file(obj, path=None):
    """
    Looks at a CSV file and overwrites data in database
    """
    from cli.openapply_importer import OA_Medical_Importer

    f = path or gns.config.paths.medical_info
    medical_importer = OA_Medical_Importer.from_file(f)
    medical_importer.read_in()

@sync.command()
@click.option('path', '--path', type=click.Path(exists=True))
@click.pass_obj
def openapply_from_api(obj, path=None):
    """
    Looks at a CSV file and overwrites data in database
    """ 
    from cli.openapply_importer import OA_Medical_Importer

    f = path or gns.config.paths.medical_info
    medical_importer = OA_Medical_Importer.from_api()
    medical_importer.read_in()

def run_scraper(spider, subpath, **kwargs):

    import scrapy
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    os.chdir(os.path.join(gns.config.paths.scrapers, subpath))

    settings = get_project_settings()
    # Chance here to mod settings
    if kwargs.get('--nolog'):
        gns.tutorial("Turned off scrapy's logging with LOG_ENABLED")
        settings['LOG_ENABLED'] = 0

    process = CrawlerProcess(settings)
    process.crawl(spider, **kwargs)  # TODO: add kwargs here for options
    process.start()


@main.group()
@click.pass_context
# @click.option('--student_id', default=None, help="MB student ID of student")
# @click.option('--student_name', default=None, help="MB name of student in lastfirst style")
# @click.option('--grade', default=None, help="Ex) Early Years 2")
def pyp_reports(ctx):
    """
    Commands for implementing PYP Reports
    """
    pass


@pyp_reports.command('save')
@click.option('--check', is_flag=True, default=False, help="Launch a check instead")
@click.option('--students', multiple=True, default=[], help="all for everyone")
@click.option('--grades', multiple=True, default=[], help="")
@click.option('--classes', multiple=True, default=[], help="")
@click.pass_obj
def pyp_reports_save(obj, check, students, grades, classes):
    from sqlalchemy.orm.exc import NoResultFound
    import gns
    import re
    from sqlalchemy import and_

    import requests

    db = Database()
    Students = db.table_string_to_class('Student')
    Parents = db.table_string_to_class('Parent')
    PrimaryReport = db.table_string_to_class('primary_report')

    class DoIt:
        base_url = 'http://igbisportal.vagrant:6543/students/{student_id}/pyp_report/download?api_token={api_token}'

        def __init__(self, one_student=None, one_grade=None):
            if one_student:
                self.filter = Students.student_id == one_student
            elif one_grade:
                self.filter = Students.class_grade == one_grade
            else:
                self.filter = None

        def go(self, starting_from=None):

            api_token = gns.config.managebac.api_token
            with DBSession() as session:
                if self.filter is not None:

                    students = session.query(
                        Students
                    ).filter(
                        self.filter
                    ).order_by(
                        Students.grade
                    ).all()

                else:
                    students = session.query(
                        Students
                    ).filter(
                        Students.grade < 6,
                        Students.is_archived == False,  # FIXME: This has never made much sense to me
                        Students.student_id is not None
                    ).order_by(
                        Students.grade
                    ).all()

                    if starting_from:
                        index = [i for i in range(len(students)) if students[i].student_id == starting_from]
                        if index:
                            index = index[0]
                            students = students[index:]
                        else:
                            students = []

                for student in students:
                    try:
                        report = session.query(PrimaryReport).filter_by(id=student.id)
                    except NoResultFound:
                        # raw_input('no report!')
                        continue

                    report  # not used
                    url = self.base_url.format(student_id=student.id, api_token=api_token)
                    r = requests.get(url)

                    if r.status_code == 200:
                        if not check:
                            print("All is well with {}".format(student))
                        # print(r.url)

                    if r.status_code != 200:
                        # print(url.replace('localhost', 'igbisportal.vagrant'))
                        text = r.text
                        message = re.findall('##(.*)##', text, re.DOTALL)
                        if message:
                            print(message[0])
                        else:
                            self.output("Nope {}: {}, {}".format(r.status_code, student.student_id, url))

        def dates(self):
            """ FIXME is this used? if so, how """
            term_id = gns.config.managebac.current_term_id

            base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download?api_token={api_token}'

            import portal.settings as settings

            api_token = settings.get('MANAGEBAC', 'mb_api_token')

            with DBSession() as session:
                if self.filter is not None:
                    parents = session.query(Parents).filter(self.filter).all()
                else:
                    parents = session.query(Parents).all()

                for parent in parents:
                    parent.google_account_sunset('1 month')
            print('Done!')

        def output(self, msg):
            print(msg)

    class CheckIt(DoIt):

        base_url = 'http://localhost:6543/students/{student_id}/pyp_report/download?api_token={api_token}&check=True'

        def output(self, msg):
            pass

    for student in students:
        if student == "all":
            do = CheckIt() if check else DoIt()
        else:
            do = CheckIt(one_student=student) if check else DoIt(one_student=student)
        do.go()

    for grade in grades:
        if grade == "all":
            do = CheckIt() if check else DoIt()
        else:
            do = CheckIt(one_grade=grade) if check else DoIt(one_grade=grade)
        do.go()

    for class_ in classes:
        if class_ == "all":
            do = CheckIt() if check else DoIt()
            do.go()
        else:
            with DBSession() as session:
                students = session.query(
                    db.table.Student.student_id
                ).select_from(
                    db.table.Student
                ).join(
                    db.table.Enrollment,
                    db.table.Enrollment.c.student_id == db.table.Student.id
                ).filter(
                    db.table.Course.uniq_id == class_
                )
                for student in students.all():
                    do = CheckIt(one_student=student) if check else DoIt(one_student=student)
                    do.go()


@pyp_reports.group('scrape')
@click.option('--log/--nolog', default=True, help="Toggle logging")
@click.pass_context
def pyp_reports_scrape(ctx, log):
    """
    Download info
    """
    # Whenever we scape, we want to make it play nice with other processes
    ctx.obj.logging = {'LOG_ENABLED': int(log)}
    os.nice(15)

    # Limit execution time to one hour
    import resource
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (3600, 4000)
    )


@pyp_reports_scrape.command('reports')    
@click.option('--this_student', default=None, help="MB student ID of student")
@click.option('--callback_id', default=None, help="Internal use only")
@click.option('--fake', is_flag=True, default=False, help="Make fake data")
@click.pass_obj
def pyp_reports_scrape_reports(obj, this_student, callback_id, fake):
    """
    This program will download PYP report data as entered
    by teachers from ManageBac
    """
    gns.tutorial(pyp_reports_scrape_reports.__doc__)
    kwargs = obj.logging
    kwargs['fake'] = fake
    if this_student is not None:
        # Use the db to get the student id and relevant class id in order
        db = Database()

        with DBSession() as session:
            statement = session.query(
                db.table.Student.id, db.table.Course.id
            ).select_from(
                db.table.Student
            ).join(
                db.table.Enrollment,
                db.table.Enrollment.c.student_id == db.table.Student.id
            ).join(
                db.table.Course,
                db.table.Course.id == db.table.Enrollment.c.course_id
            ).filter(
                db.table.Student.student_id == this_student
            )
            gns.tutorial("Collecting data for only one student", edit=(statement, '.sql'), stop=True)
            results = statement.all()

            if len(results) == 1:
                student_id, class_id = results[0]
                gns.tutorial("Got the student mb id ({}) and the course id ({}) they are enrolled in.".format(student_id, class_id))
                kwargs.update(dict(student_id=student_id, class_id=class_id))
            elif len(results) == 0:
                print("No classes, is the ID right?")
                return
            else:
                print("More than one class?")
                return

    gns.tutorial("Sending to scraper with kwargs: {}".format(kwargs))
    run_scraper('PYPClassReports', 'pyp_class_reports', **kwargs)

    if callback_id:
        gns.tutorial("Need to update the callback with uniq_id = {}".format(callback_id))
        with DBSession() as session:
            record = session.query(
                db.table.Callback
            ).filter(
                db.table.Callback.uniq_id == callback_id
            ).one()
            record.done = True


@pyp_reports_scrape.command('teacher_assign')
def pyp_reports_scrape_teacher_assign():
    """
    Download the teacher assignment info
    """
    run_scraper('PYPTeacherAssignments', 'pyp_teacher_assignments')


@pyp_reports_scrape.command('student_attendance')
def pyp_reports_scrape_student_attendance():
    """
    Download the teacher assignment info
    """
    run_scraper('PYPStudentAttendance', 'pyp_student_attendance')


@main.group()
def utils():
    """
    Commands that form another category
    """
    pass


@utils.command()
def serve():
    """
    Launches the webserver for debugging
    """
    import subprocess
    click.echo("'screen -ls'")
    subprocess.call(['screen', '-ls'])
    confirm = click.confirm("Create screen called 'pserve'?")
    if not confirm:
        return
    os.chdir(gns.config.paths.frontend_home)
    deploy_file = os.path.join(gns.config.paths.frontend_home, 'production.ini')
    # screen -ls | grep pserve
    subprocess.call(['screen', '-dm', '-S', 'pserve'])
    subprocess.call(['screen', '-r', 'pserve', '-X', 'stuff', 'pserve --reload {}\n'.format(deploy_file)])
    click.echo(message="Deployed: " + "'screen -r pserve' to view server output")


@utils.command()
def create_all_tables():
    from portal.db import metadata, engine
    metadata.create_all(engine)
    print('Done: metadata.create_all(engine)')


@main.group()
def debug():
    return


@debug.command()
@click.argument('id')
@click.pass_context
def teacher_classes(ctx, id):
    if id == 'yuri':
        id = 10792610
    from portal.db import Database, DBSession
    db = Database()

    Teachers = db.table_string_to_class('advisor')

    with DBSession() as session:
        user = session.query(Teachers).filter(Teachers.id == 10792610).one()
        if not user:
            print(dict(message="No user in session?"))
        if not hasattr(user, 'classes'):
            print(dict(message="User doesn't have classes?"))
        data = []
        for klass in user.classes:
            grade_str = re.search('\((.*?)\)', klass.name)
            if grade_str:
                str = grade_str.group(1)
                grade_str = {'Grade 10': 10, 'Grade 11': 11, 'Grade 12': 12}.get(str, int(re.sub('[^0-9]', '', str)))
            else:
                grade_str = ""
            data.append(dict(name=klass.abbrev_name, sortby=(grade_str, klass.uniq_id), shortname=klass.uniq_id, link='https://igbis.managebac.com/classes/{}'.format(klass.id)))
        for item in sorted(data, key=lambda x: x['sortby'], reverse=True):
            print(item['name'])


@main.group()
def test():
    """
    Commands for testing purposes
    """
    pass


@test.command('api_family_info')
@click.pass_obj
def test_family_info(obj):
    options = {
        'secret': 'phillies',
        'human_columns': True,
        'google_sheets_format': True,
        'column_map': {},
        'columns': ['email', 'grades_taught']
    }

    url = 'http://localhost:6543/api/family_info'
    result = requests.post(url, json=options)
    print(result)
    print(result.json())


@test.command('test_status_updater')
@click.pass_obj
def test_status_updater(obj):
    from portal.db.interface import DatabaseSetterUpper
    go = DatabaseSetterUpper(lazy=True, verbose=True)
    go.update_status()


@test.command('test_api_downloader')
@click.pass_obj
def test_api_downloader(obj):
    from portal.db.api.interface import APIDownloader
    dl = APIDownloader()
    dl.download_all()
    from portal.db.interface import DatabaseSetterUpper
    go = DatabaseSetterUpper(lazy=True, verbose=True)
    go.setup_database()


@test.command('test_db')
@click.argument('_id', default=11204340)  # Fern
@click.pass_obj
def test_db(obj, _id):
    from portal.db import Database, DBSession
    db = Database()
    Teachers = db.table_string_to_class('advisor')
    from sqlalchemy.orm import joinedload

    with DBSession() as session:
        teachers = session.query(Teachers).options(joinedload('classes')).all()

    from IPython import embed;embed()


@test.command('inspect_student')
@click.pass_obj
def inspect_student(obj):
    from portal.db import Database, DBSession
    from sqlalchemy.orm import joinedload, joinedload_all

    db = Database()
    Students = db.table_string_to_class('student')

    with DBSession() as session:

        query = session.query(Students).\
            options(joinedload('parents')).\
            options(joinedload('ib_groups')).\
            options(joinedload_all('classes.teachers')).\
            filter(Students.student_id == '20220018').\
            order_by(Students.first_name)

        result = query.one()

        from IPython import embed;embed()


@test.command('api_students')
@click.option('--column', multiple=True, default=None, help="Any of the hybrid properties")
@click.option('--destiny', is_flag=True, default=False, help="Use destiny columns (overrides columns)")
@click.option('--every_column', is_flag=True, default=False, help="Test everything!")
@click.option('--order_by', default=False, help="Order by column")
@click.option('--inspect', is_flag=True, default=False, help="runs IPyton at end")
@click.option('--output_sids', default=None, help="string of student ids with spaces")
@click.pass_obj
def test_api_students(obj, column, destiny, every_column, order_by, inspect, output_sids):
    if destiny:
        column = ['student_id', 'barcode', 'homeroom_teacher_email', 'homeroom_full', 'program_of_study', 'destiny_site_information', 'destiny_patron_type', 'username', 'last_name', 'first_name', 'nickname', 'class_grade', 'email', 'gender', 'parent_email_1', 'year_of_graduation']
    if column is None:
        print("No columns..")
        return

    options = {
        'secret': 'phillies',
        'awesome_table_filters': {'student': 'StringFilter', 'grade': 'CategoryFilter'},
        'human_columns': True,
        'google_sheets_format': True,
        'column_map': {'health_information': 'Health Info!'},
        'columns': column,
    }

    if every_column:
        options['every_column'] = True
    if order_by:
        options['order_by'] = order_by

    #url = 'http://portal.igbis.edu.my/api/students'
    url = 'http://localhost:6543/api/students'
    print(options)
    result = requests.post(url, json=options)
    if not result.ok:
        print("Bad result: {}".format(result.status_code))
        print(result.text)
        return
    json = result.json()
    for data in json['data']:
        if not output_sids is None:
            i = int(output_sids.split(' ')[0])
            if data[i] in output_sids.split(' ')[1:]:
                print(data)
        else:
            print(data)
    if inspect:
        from IPython import embed;embed()

    for data in json['data']:
        pass


@test.command('api_teachers')
@click.option('--columns')
@click.pass_obj
def test_api_teachers(obj):
    options = {
        'secret': 'phillies',
        'human_columns': True,
        'google_sheets_format': True,
        'column_map': {},
        'columns': ['email', 'grades_taught']
    }

    #url = 'http://portal.igbis.edu.my/api/students'
    url = 'http://localhost:6543/api/teachers'
    result = requests.post(url, json=options)
    print(result.json())
    from IPython import embed;embed()


@main.group()
@click.pass_context
def _one_time(ctx):
    """
    Commands intended to be launched once, kept for posterity
    """
    pass


@_one_time.command('igbis_email_transition')
@click.option('--dry/--wet', default=True, help="dry run by default only outputs")
@click.pass_obj
def igbis_email_transition(obj, dry):
    """
    One-time operation to transition parents into our Google domain
    """
    from portal.db import Database, DBSession
    db = Database()
    Parents = db.table_string_to_class('parent')

    with DBSession() as session:

        parents = session.query(Parents)  # .filter(Parents.id==10882228)

        for parent in parents.all():
 
            # Set up to the url to use the user id
            # ... and also the authorization token which will be passed to requests module
            gns.user_id = parent.id
            url = gns('{config.managebac.url}/api/users/{user_id}')
            # url = gns('{config.managebac.url}/api/v1/users/{user_id}/')

            # Save the old email
            old_email = parent.email or ''

            # Check that we haven't already changed this
            if '.parent@igbis.edu.my' not in old_email:
                # ... keep going then
                new = {}
                new['email'] = parent.igbis_email_address

                # We lose the previous work_email...
                if not parent.work_email:
                    new['work_email'] = old_email
                else:
                    if parent.work_email != old_email:
                        new['work_email'] = old_email + ',' + parent.work_email
                    else:
                        new['work_email'] = old_email

                if dry:
                    if new['work_email']:
                        print("{},{}".format(new['email'], new['work_email']))
                    else:
                        pass
                        # print("Changed email to {}".format(new['email']))
                else:
                    result = requests.put(url, headers={'auth_token': gns.config.managebac.api_token}, json={'user': new})
                    print('{} {}'.format(result.status_code, result.url))
                    # result = requests.put(url, headers={'auth_token': gns.config.openapply.api_token}, json={'user':new})
                    # from IPython import embed
                    # embed()
            else:
                pass
                # print("Did not update {} because it is already updated".format(parent))


@main.group()
@click.pass_context
def test_api(ctx):
    pass


@test_api.command('managebac')
@click.argument('_id', default=10882228, )
@click.argument('field', default="")
@click.argument('value', default="")
@click.pass_obj
def test_managebac_api(obj, _id, field, value):
    from portal.db import Database, DBSession
    db = Database()
    Parents = db.table_string_to_class('parent')

    with DBSession() as session:

        parents = session.query(Parents).filter(Parents.id==_id)

        for parent in parents.all():
 
            # Set up to the url to use the user id
            # ... and also the authorization token which will be passed to requests module
            gns.user_id = parent.id
            params = {'auth_token': gns.config.managebac.api_token}
            url = gns('{config.managebac.url}/api/users/{user_id}')
            # url = gns('{config.managebac.url}/api/v1/users/{user_id}/')

            result = requests.get(url, params=params)
            print(result.json())


@test_api.command('managebac_get')
@click.argument('_id', default=11286952)  #11286952 = DongJune #10875405
@click.pass_obj
def test_managebac_get(obj, _id):
    from portal.db import Database, DBSession
    db = Database()

    # Set up to the url to use the user id
    # ... and also the authorization token which will be passed to requests module
    gns.user_id = _id
    params = {'auth_token': gns.config.managebac.api_token}
    url = gns('{config.managebac.url}/api/users/{user_id}')

    result = requests.get(url, params=params)
    from IPython import embed;embed()

    print(result.json())


@test_api.command('managebac_put')
@click.argument('_id', default=10868315)  #10875405
@click.pass_obj
def test_managebac_put(obj, _id):
    from portal.db import Database, DBSession
    db = Database()

    # Set up to the url to use the user id
    # ... and also the authorization token which will be passed to requests module
    gns.user_id = _id
    params = {'auth_token': gns.config.managebac.api_token}
    url = gns('{config.managebac.url}/api/users/{user_id}')

    new = {'work_phone': 'success'}   #Magical Era (M) Sdn Bhd

    result = requests.put(url, headers={'auth_token': gns.config.managebac.api_token}, json={'user': new})

    print(result.json())


@test_api.command('openapply_get')
@click.argument('_id', default=27943)  # 10875405
@click.pass_obj
def test_openapply_get(obj, _id):

    # Set up to the url to use the user id
    # ... and also the authorization token which will be passed to requests module
    gns.user_id = _id
    params = {'auth_token': gns.config.openapply.api_token}
    url = gns('{config.openapply.url}/api/v1/students/{user_id}')

    result = requests.get(url, params={'auth_token': gns.config.openapply.api_token})
    from IPython import embed;embed()
    print(result.json())
    print(result.json()['student']['status'])


@test_api.command('openapply_put')
@click.argument('_id', default=27943)
@click.pass_obj
def test_openapply_put(obj, _id):
    from portal.db import Database
    db = Database()
    Parents = db.table_string_to_class('parent')

    # Set up to the url to use the user id
    # ... and also the authorization token which will be passed to requests module
    gns.user_id = _id
    url = gns('{config.openapply.url}/api/v1/students/{user_id}/status')

    new = {}
    new['status'] = 60

    result = requests.put(url, params={'auth_token': gns.config.openapply.api_token}, json=new)
    from IPython import embed;embed()
    print(result.json())
    print(result.json()['student']['status'])


@main.group()
@click.pass_obj
def status(obj):
    """
    Commands that compare and contrast
    """
    pass


@status.command('compare')
@click.pass_obj
def compare(obj):
    """
    Compare parents on google with those in database?
    """
    from portal.db import Database, DBSession
    db = Database()
    from sqlalchemy.orm import joinedload

    Parents = db.table_string_to_class('parent')
    Students = db.table_string_to_class('student')
    google_users = []
    with open('/home/vagrant/igbisportal/lastlogins.txt') as f:
        reader = csv.reader(f)
        headers = reader.next()
        for row in reader:
            google_users.append(row[0])
    google_parents = [p for p in google_users if 'parent@' in p]

    mb_parents = []
    with DBSession() as session:
        students = session.query(Students).\
            options(joinedload('parents')).\
            filter(not Students.archived==True).\
            all()
        for student in students:
            parents = student.parents
            for parent in parents:
                if parent.email and 'parent@' in parent.email:
                    mb_parents.append(parent.email)

    print('# Existing parents in google: {}'.format(len(set(google_parents))))
    print('# Existing parents in manage: {}'.format(len(set(mb_parents))))

    print('google - mb:')
    gmm = set(google_parents) - set(mb_parents)
    mmg = set(mb_parents) - set(google_parents)
    print('\n'.join(gmm))
    print()
    print('mb - google:')
    print('\n'.join(mmg))
    print()
    from IPython import embed;embed()


