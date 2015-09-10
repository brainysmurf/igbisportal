from distutils.core import setup
setup(
    name = "IGBIS Portal",
    #packages = ['db'],
    version = "1.5",
    description = "A front end to all the front ends",
    author = "Adam Morris",
    author_email = "amorris@mistermorris.com",
    keywords = [],
    packages=['cli', 'portal', 'gns'],
    entry_points='''
        [console_scripts]
        portal=cli.main:main
    ''',
    install_requires = ['sqlalchemy', 'scrapy',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'service_identity',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'requests',
    'psycopg2',
    'python-dateutil'
],
    # also requires?
    #'scrapyd', 'lxml', 'w3lib', 'cssselect', 'pysqlite'


    # classifiers = [
    #     "Programming Language :: Python",
    #     "Programming Language :: Python :: 3",
    #     "Development Status :: 4 - Beta",
    #     "Intended Audience :: Developers",
    #     "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    #     "Operating System :: OS Independent",
    #     ],
    long_description = """\
TODO: DESCRIBE THIS!


"""
)
