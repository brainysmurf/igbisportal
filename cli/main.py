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
def first_launch(obj, download, setupdb):
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

def scrape_all():
    from scrapy import cmdline
    from portal.settings import get
    path = get('DIRECTORIES', 'path_to_scrapers', required=True)
    import os, gns

    os.chdir(gns('{settings.path_to_scrapers}/mb_scraper'))
    cmdline.execute(['scrapy', 'crawl', 'ClassPeriods'])
    os.chdir(gns('{settings.path_to_scrapers}/oa_scraper'))
    cmdline.execute(['scrapy', 'crawl', 'AuditLog'])

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