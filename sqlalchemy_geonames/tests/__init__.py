from nose.tools import eq_, assert_greater
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from .. import GeonameBase, get_importer_instances
from ..imports import _import_options_map

test_filenames = (
    'cities1000.txt',
    'timeZones.txt',
    'featureCodes_en.txt',
    'countryInfo.txt',
)

connstr = ('postgresql+psycopg2://sqla_geonames:sqla_geonames@'
           'localhost:5432/sqla_geonames')
engine = create_engine(connstr)
session_factory = sessionmaker(autocommit=False, autoflush=False)
Session = scoped_session(session_factory)
Session.configure(bind=engine)


def get_tst_filepath(filename):
    return os.path.join(os.path.dirname(__file__), 'files', filename)


GeonameBase.metadata.drop_all(bind=engine)
GeonameBase.metadata.create_all(bind=engine)


class TestBase(object):

    def setup(self):
        """Run at the start of each test
        NOTE: You need to set up a postgresql database with postgis extension.
              See tests/bin/create_testdb.sh for how to do this. Or run
              as is if you're a daredevil!
        """
        self.session = Session()

    def teardown(self):
        self.session.close()

    def test_import_ordering(self):
        filenames = ['cities1000.txt', 'countryInfo.txt']
        filepaths = [get_tst_filepath(fn) for fn in filenames]
        importers = get_importer_instances(self.session, *filepaths)
        eq_(importers[0].filename, 'countryInfo.txt')

        filenames = ['featureCodes_en.txt', 'cities1000.txt',
                     'countryInfo.txt']
        filepaths = [get_tst_filepath(fn) for fn in filenames]
        importers = get_importer_instances(self.session, *filepaths)
        eq_(importers[-1].filename, 'cities1000.txt')

    def test_filereaders(self):
        for filename in test_filenames:
            filepath = get_tst_filepath(filename)
            file_class = _import_options_map[filename].file_class
            # list iterates the GeonameFile-subclass
            file_reader = file_class(filepath)
            field_names = set(file_reader.field_names)
            for row in file_reader:
                eq_(set(row.keys()), field_names)

    def test_imports(self):
        filepaths = [get_tst_filepath(fn) for fn in test_filenames]
        importers = get_importer_instances(self.session, *filepaths)
        for importer in importers:
            importer.run()
            assert_greater(self.session.query(importer.model).count(), 1)
