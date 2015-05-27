import click
from portal.db import Database, DBSession

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

@main.command()
@click.option('--download/--dontdownload', default=True, help='default is not_lazy')
@click.option('--setupdb/--dontsetupdb', default=True, help='default is not_lazy')
@click.pass_obj
def push(obj, download, setupdb):
    """
    Downloads initial data from ManageBac APIs and via scraping
    """
    dl(lazy=not download, verbose=obj.verbose)
    db_setup(lazy=not setupdb, verbose=obj.verbose)

@main.group()
def api():
    """
    Commands to download from API and populate database from API
    """
    pass

@api.command()
@click.option('--lazy/--not_lazy', default=False, help='default is not_lazy')
@click.confirmation_option('--yes', '-y', help='Silence confirmation to delete', expose_value=False, prompt="This operation deletes jsons that may have been previously downloaded. Continue?")
@click.pass_obj
def download(obj, lazy):
    """
    Downloads from API
    """
    dl(lazy, obj.verbose)

@api.command()
@click.option('--lazy/--not_lazy', default=False, help='default is not_lazy')
@click.pass_obj
def populate_database(obj, lazy):
    """
    Populates Postgres database from downloaded API
    """
    db_setup(lazy, obj.verbose)


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

@main.command()
def scrape_pyp_assignments():
    from portal.scrapers.mb_scraper.mb_scraper.spiders.ClassPeriods import PYPTeacherAssignments
    run_scraper(PYPTeacherAssignments, 'mb_scraper')

    # os.chdir(gns('{settings.path_to_scrapers}/oa_scraper'))
    # cmdline.execute(['scrapy', 'crawl', 'AuditLog'])

@main.command()
def scrape_pyp_reports():
    from portal.scrapers.mb_scraper.mb_scraper.spiders.ClassPeriods import PYPClassReports
    run_scraper(PYPClassReports, 'mb_scraper')

@main.command()
def scrape():
    """
    Commands to fetch and populate postgres database
    """
    scrape_all()

@main.command()
def serve():
    """
    Launches the webserver for debugging
    """
    import subprocess
    subprocess.call(['pserve', '--reload', '/home/vagrant/igbisportal/development.ini'])

@main.command()
def create_all_tables():
    from portal.db import metadata, engine
    metadata.create_all(engine)
    print('Done: metadata.create_all(engine)')

@click.option('--class_id', default=None)
@main.command()
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
