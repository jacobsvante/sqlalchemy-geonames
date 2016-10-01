#!/usr/bin/env python
"""
sqlalchemy-geonames
-------------------

"""
from __future__ import print_function
from setuptools import setup, find_packages


appname = 'sqlalchemy-geonames'
pkgname = appname.lower().replace('-', '_')
metadata_relpath = '{}/metadata.py'.format(pkgname)

# Get package metadata. We use exec here instead of importing the
# package directly, so we can avoid any potential import errors.
with open(metadata_relpath) as fh:
    metadata = {}
    exec(fh.read(), globals(), metadata)


setup(
    name=appname,
    version=metadata['__version__'],
    description='',
    long_description=__doc__,
    packages=find_packages(exclude=('sqlalchemy_geonames.tests', )),
    install_requires=[
        'SQLAlchemy>=0.8',
        'GeoAlchemy2>=0.2.3',
        'requests>=2.0',
        'psycopg2>=2.5',
        # This install is recommended for performance, but not required.
        # For pip 1.5+ you need to install with `pip install --allow-external cdecimal`
        # as external urls are no longer allowed by default.
        # cdecimal>=2.3

        # NOTE: python-progressbar is not yet py3.3 compatible as of 4 jan 2014.
        #       Use progressbar2 instead (fork of progressbar).
        'progressbar2>=2.6',
    ],
    entry_points={
        'console_scripts': {
            'sqlageonames = sqlalchemy_geonames.bin.sqlageonames:main',
        },
    },
    author='Jacob Magnusson',
    author_email='m@jacobian.se',
    url='https://github.com/jmagnusson/sqlalchemy-geonames',
    license='BSD',
    platforms=['unix', 'macos'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
    ],
)
