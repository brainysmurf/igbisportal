import click
import gns
import os

class Object(object):
    def __init__(self):
        # chance to get setings
        pass

    # define common methods here

#
# Define global options here
#
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
def parent_accounts(obj):
    from cli.parent_accounts import ParentAccounts
    parent_accounts = ParentAccounts()
    parent_accounts.output_()

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
def openapply(obj, path=None):
    """
    Looks at a CSV file and overwrites data in database
    """
    from cli.openapply_importer import OA_Medical_Importer

    f = path or gns.config.paths.medical_info
    medical_importer = OA_Medical_Importer(f)
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
    import re

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



