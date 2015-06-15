import click

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
    parent_accounts.output()

@sync.command()
@click.option('path', '--path', type=click.Path(exists=True))
@click.pass_obj
def openapply(obj, path=None):
    """
    Looks at a CSV file and overwrites data in database
    """
    if not path:
        import portal.settings as settings
        f = settings.get('DIRECTORIES', 'path_to_medical_info')
    from cli.openapply_importer import OA_Medical_Importer
    medical_importer = OA_Medical_Importer(f)
    medical_importer.read_in()

def run_scraper(spider, subpath):
    from portal.settings import get
    import os, gns

    path = get('DIRECTORIES', 'path_to_scrapers', required=True)
    gns.subpath = subpath
    os.chdir(gns('{settings.path_to_scrapers}/{subpath}'))

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
    import os
    from portal.settings import get
    import gns
    path = get('DIRECTORIES', 'path_to_scrapers', required=True)

    os.chdir(gns('{settings.path_to_scrapers}/mb_scraper'))

    if not class_id:
        cmdline.execute(['scrapy', 'crawl', 'PYPTeacherAssignments'])
        cmdline.execute(['scrapy', 'crawl', 'PYPClassReports'])
    else:
        cmdline.execute(['scrapy', 'crawl', 'PYPTeacherAssignments', '-a', 'class_id={}'.format(class_id)])
        from IPython import embed
        embed()
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


