from distutils.core import setup
setup(
    name = "IGBIS Portal",
    packages = ['db'],
    version = "1.0",
    description = "A front end to all the front ends",
    author = "Adam Morris",
    author_email = "amorris@mistermorris.com",
    keywords = [],
    install_requires = ['sqlalchemy', 'scrapy'],
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
