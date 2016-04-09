import click
import gns
import os, datetime
import requests, json
import re, csv

class Object(object):
    def __init__(self):
        # chance to get setings
        pass

    # define common methods here

@click.group()
@click.option('--verbose/--not_verbose', default=False, help="Outputs loads more info")
@click.pass_context
def main(ctx, verbose):
    # Doesn't do much now, but leave it as boilerplate for when there are global flags n such
    ctx.obj = Object()
    ctx.obj.verbose = verbose

def dl(lazy=False, verbose=False):
    from portal.db.api.interface import APIDownloader
    go = APIDownloader(lazy=lazy, verbose=verbose)    

def db_setup(lazy, verbose):
    from portal.db.interface import DatabaseSetterUpper
    go = DatabaseSetterUpper(lazy=lazy, verbose=verbose)

@main.group()
def sync():
    """
    Commands that launches syncing with MB and OA
    """
    pass

@sync.command()
@click.option('--download/--dontdownload', default=True, help='default is --download')
@click.option('--setupdb/--dontsetupdb', default=True, help='default is --setupdb')
@click.pass_obj
def managebac(obj, download, setupdb):
    """
    Downloads data from ManageBac APIs, and updates database
    """
    dl(lazy=not download, verbose=obj.verbose)
    db_setup(lazy=not setupdb, verbose=obj.verbose)

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
def student_columns(obj):
    from portal.db import Database, DBSession
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

def run_scraper(spider, subpath):

    os.chdir(gns('{config.paths.scrapers}/{subpath}'))

    from twisted.internet import reactor
    from scrapy.crawler import Crawler
    from scrapy.utils.project import get_project_settings
    from scrapy import log, signals
    settings = get_project_settings()

    sp = spider()
    crawler = Crawler(settings)
    crawler.configure()
    crawler.crawl(sp)
    crawler.start()  

    log.start()
    reactor.run()

@main.group()
def scrape():
    """
    Commands to fetch and populate postgres database
    """
    pass

@scrape.command()
def pyp_reports():
    from portal.scrapers.mb_scraper.mb_scraper.spiders.ClassPeriods import PYPClassReports
    run_scraper(PYPClassReports, 'mb_scraper')

@scrape.command()
@click.option('--class_id', default=None)
def pyp_reports(class_id):
    """
    Sets up things for pyp reporting system
    """
    from scrapy import cmdline

    os.chdir(gns('{settings.path_to_scrapers}/mb_scraper'))

    if not class_id:
        cmdline.execute(['scrapy', 'crawl', 'PYPTeacherAssignments'])
        cmdline.execute(['scrapy', 'crawl', 'PYPClassReports'])
    else:
        cmdline.execute(['scrapy', 'crawl', 'PYPTeacherAssignments', '-a', 'class_id={}'.format(class_id)])
        cmdline.execute(['scrapy', 'crawl', 'PYPClassReports', '-a', 'class_id={}'.format(class_id)])

@scrape.command()
def pyp_assignments():
    from portal.scrapers.mb_scraper.mb_scraper.spiders.ClassPeriods import PYPTeacherAssignments
    run_scraper(PYPTeacherAssignments, 'mb_scraper')

    # os.chdir(gns('{settings.path_to_scrapers}/oa_scraper'))
    # cmdline.execute(['scrapy', 'crawl', 'AuditLog'])

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
    subprocess.call(['pserve', '--reload', '/home/vagrant/igbisportal/development.ini'])

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
            data.append( dict(name=klass.abbrev_name, sortby=(grade_str, klass.uniq_id), shortname=klass.uniq_id, link='https://igbis.managebac.com/classes/{}'.format(klass.id)) )
        for item in sorted(data, key=lambda x: x['sortby'], reverse=True):
            print(item['name'])

@main.group()
def test():
    pass

@test.command('test_db')
@click.argument('_id', default=11204340) # Fern
@click.pass_obj
def test_db(obj, _id):  
    from portal.db import Database, DBSession
    db = Database()
    Students = db.table_string_to_class('student')

    with DBSession() as session:
        student = session.query(Students).filter(Students.id==_id).one()
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
            filter(Students.student_id=='20220018').\
            order_by(Students.first_name)

        result = query.one()

        from IPython import embed;embed()

@test.command('api_students')
@click.option('--columns', default=None, help="Any of the hybrid properties")
@click.option('--destiny', is_flag=True, default=False, help="Use destiny columns (overrides columns)")
@click.option('--every_column', is_flag=True, default=False, help="Test everything!")
@click.option('--inspect', is_flag=True, default=False, help="runs IPyton at end")
@click.option('--output_sids', default=None, help="string of student ids with spaces")
@click.pass_obj
def test_api_students(obj, columns, destiny, every_column, inspect, output_sids):
    if destiny:
        columns = ['student_id', 'barcode', 'homeroom_teacher_email', 'homeroom_full', 'program_of_study', 'destiny_site_information', 'destiny_patron_type', 'username', 'last_name', 'first_name', 'nickname', 'class_grade', 'email', 'gender', 'parent_email_1', 'year_of_graduation']
    if every_column:
        columns = ['student_id', 'first_name', 'last_name', 'gender', 'nationality1', 'nationality2', 'nationality3', 'nationality4', 'phone_number', 'mobile_phone_number', 'national_id', 'email', 'language', 'lanuage1', 'language2', 'language3', 'program', 'program_of_study', 'class_year', 'grade', 'class_grade', 'grade_range', 'archived', 'nickname', 'attendance_start_date', 'birthday', 'open_apply_student_id', 'homeroom_advisor', 'profile_photo', 'year_of_graduation', 'parent_emails', 'parent_names', 'parent_name_1', 'parent_name_2', 'parent_email_1', 'parent_email_2', 'parent_work_email_1', 'parent_work_email_2', 'parent_contact_info', 'teacher_emails', 'teacher_usernames', 'nickname_last_studentid', 'last_first_nickname_studentid', 'grade_last_first_nickname_studentid', 'first_nickname_last_studentid', 'first_nickname_last', 'first_nickname', 'grade_first_nickname_last_studentid', 'abbrev_grade', 'health_information', 'emergency_info', 'homeroom_teacher_email', 'homeroom_abbrev', 'homeroom_full', 'barcode', 'destiny_site_information', 'destiny_patron_type']
        #TODO: open_apply_student_id
    if columns is None:
        print("No columns..")
        return

    options = {
        'secret': 'phillies',
        'awesome_table_filters': {'student': 'StringFilter', 'grade': 'CategoryFilter'},
        'human_columns': True,
        'google_sheets_format': True,
        'column_map': {'health_information': 'Health Info!'}, 
        'columns': columns
    }

    #url = 'http://portal.igbis.edu.my/api/students'
    url = 'http://localhost:6543/api/students'
    result = requests.post(url, json=options)
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

@test.command('api_lastlogins')
@click.pass_obj
def test_api_lastlogins(obj):
    options = {
        'secret': 'phillies',
    }

    url = 'http://portal.igbis.edu.my/api/students'
    #url = 'http://localhost:6543/api/lastlogins'
    result = requests.post(url, json=options)
    print(result.json())
    from IPython import embed;embed()

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
def update(ctx):
    pass

@update.command('igbis_email_transition')
@click.option('--dry/--wet', default=True, help="dry run by default only outputs")
@click.pass_obj
def igbis_email_transition(obj, dry):
    from portal.db import Database, DBSession
    db = Database()
    Parents = db.table_string_to_class('parent')

    with DBSession() as session:

        parents = session.query(Parents) #.filter(Parents.id==10882228)

        for parent in parents.all():
 
            # Set up to the url to use the user id
            # ... and also the authorization token which will be passed to requests module
            gns.user_id = parent.id
            params = {'auth_token': gns.config.managebac.api_token}
            url = gns('{config.managebac.url}/api/users/{user_id}')
            #url = gns('{config.managebac.url}/api/v1/users/{user_id}/')

            # Save the old email
            old_email = parent.email or ''

            # Check that we haven't already changed this
            if not '.parent@igbis.edu.my' in old_email:
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
                        #print("Changed email to {}".format(new['email']))
                else:
                    result = requests.put(url, headers={'auth_token': gns.config.managebac.api_token}, json={'user':new})
                    print('{} {}'.format(result.status_code, result.url))
                    # result = requests.put(url, headers={'auth_token': gns.config.openapply.api_token}, json={'user':new})
                    # from IPython import embed
                    # embed()
            else:
                pass
                #print("Did not update {} because it is already updated".format(parent))

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
            #url = gns('{config.managebac.url}/api/v1/users/{user_id}/')

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

    result = requests.put(url, headers={'auth_token': gns.config.managebac.api_token}, json={'user':new})

    print(result.json())

@test_api.command('openapply_get')
@click.argument('_id', default=27943)  #10875405
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
    from portal.db import Database, DBSession
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
    pass

@status.command('compare')
@click.pass_obj
def compare(obj):
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



