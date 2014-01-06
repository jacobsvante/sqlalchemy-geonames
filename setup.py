#!/usr/bin/env python
"""
sqlalchemy-geonames
-------------------

"""
from __future__ import print_function
from pip.req import parse_requirements
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
    install_requires=[str(ir.req) for ir
                      in parse_requirements('requirements.txt')],
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
