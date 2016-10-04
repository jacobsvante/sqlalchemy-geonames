import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils.functions import (
    create_database,
    database_exists,
    drop_database
)

from sqlalchemy_geonames import GeonameBase, get_importer_instances
from sqlalchemy_geonames.imports import _import_options_map

test_filenames = (
    'cities1000.txt',
    'timeZones.txt',
    'featureCodes_en.txt',
    'countryInfo.txt',
)


def get_tst_filepath(filename):
    return os.path.join(os.path.dirname(__file__), 'files', filename)


@pytest.fixture(scope='session')
def user():
    return os.environ.get('SQLALCHEMY_GEONAMES_USER', 'postgres')


@pytest.fixture(scope='session')
def password():
    return os.environ.get('SQLALCHEMY_GEONAMES_PASSWORD')


@pytest.fixture(scope='session')
def host():
    return os.environ.get('SQLALCHEMY_GEONAMES_HOST', 'localhost')


@pytest.fixture(scope='session')
def port():
    return os.environ.get('SQLALCHEMY_GEONAMES_PORT', '5432')


@pytest.fixture(scope='session')
def dbname():
    return os.environ.get('SQLALCHEMY_GEONAMES_DBNAME', 'sqla_geonames')


@pytest.fixture(scope='session')
def dsn(user, password, host, port, dbname):
    tmpl = 'postgresql+psycopg2://{user}{password}@{host}:{port}/{dbname}'
    return tmpl.format(
        user=user,
        password=(':' + password) if password else '',
        host=host,
        port=port,
        dbname=dbname,
    )


@pytest.fixture(scope='session')
def engine(dsn):
    if database_exists(dsn):
        drop_database(dsn)
    create_database(dsn)
    engine = create_engine(dsn)
    engine.execute('CREATE EXTENSION postgis')
    GeonameBase.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope='session')
def Session(engine):
    session_factory = sessionmaker(autocommit=False, autoflush=False)
    Session = scoped_session(session_factory)
    Session.configure(bind=engine)
    return Session


@pytest.yield_fixture
def session(Session):
    """Run at the start of each test
    NOTE: You need to set up a postgresql database with postgis extension.
          See tests/bin/create_testdb.sh for how to do this. Or run
          as is if you're a daredevil!
    """
    session = Session()
    yield session
    session.close()


def test_import_ordering(session):
    filenames = ['cities1000.txt', 'countryInfo.txt']
    filepaths = [get_tst_filepath(fn) for fn in filenames]
    importers = get_importer_instances(session, *filepaths)
    assert importers[0].filename == 'countryInfo.txt'

    filenames = ['featureCodes_en.txt', 'cities1000.txt',
                 'countryInfo.txt']
    filepaths = [get_tst_filepath(fn) for fn in filenames]
    importers = get_importer_instances(session, *filepaths)
    assert importers[-1].filename == 'cities1000.txt'


def test_filereaders(session):
    for filename in test_filenames:
        filepath = get_tst_filepath(filename)
        file_class = _import_options_map[filename].file_class
        # list iterates the GeonameFile-subclass
        file_reader = file_class(filepath)
        field_names = set(file_reader.field_names)
        for row in file_reader:
            assert set(row.keys()) == field_names


def test_imports(session):
    filepaths = [get_tst_filepath(fn) for fn in test_filenames]
    importers = get_importer_instances(session, *filepaths)
    for importer in importers:
        importer.run()
        assert session.query(importer.model).count() > 1
