from __future__ import print_function
from . import reader, models, settings
from ._compat import implements_to_string

# See note in _compat for why decimal is imported
from ._compat import decimal  # noqa


@implements_to_string
class Importer(object):

    num_simoultaneous_inserts = 500

    def __str__(self):
        return '<{}Importer: {}>'.format(self.model.__name__,
                                         self.filename)
    __repr__ = __str__

    def __init__(self, options, filepath, session):
        self.filepath = filepath
        self.filename = _get_import_filename(filepath)
        self.session = session
        self.engine = session.bind
        self.stored_rows = []
        self.options = options
        self.file_class = options.file_class
        self.model = options.model
        self.table = self.model.__table__
        self.modifiers = options.modifiers
        self.model_dependencies = options.model_dependencies

    def __lt__(self, other):
        """For sorting a list of importers in the order they should run"""
        return self.model in other.model_dependencies

    def __gt__(self, other):
        return not self.__lt__(other)

    def store_rows(self):
        if not self.stored_rows:
            return
        try:
            self.engine.execute(self.table.insert(), self.stored_rows)
        except Exception as exc:
            if settings.DEBUG:
                print(exc)
                import ipdb
                ipdb.set_trace()
            else:
                raise
        finally:
            self.stored_rows = []

    def run(self):
        for i, row in enumerate(self.file_class(self.filepath)):
            for modifier in self.modifiers:
                row = modifier(self.session, self.model, row)
            self.stored_rows.append(row)
            if i % self.num_simoultaneous_inserts == 0:
                self.store_rows()
        self.store_rows()


def set_geopoint_modifier(session, model, row):
    row['point'] = u"POINT({0} {1})".format(row['latitude'],
                                            row['longitude'])
    return row


def clear_empty_fks_modifier(session, model, row):
    # Ensure empty foreign key fields is NULL instead of passing in empty
    # strings etc.
    for colname in ('feature_code', 'timezone_id', 'country_code'):
        if not row.get(colname):
            row[colname] = None
    return row


def _get_import_filename(filepath):
    return filepath.rpartition('/')[2]


@implements_to_string
class ImportOptions(object):

    def __str__(self):
        return '<{}>'.format(self.__class__.__name__)

    __repr__ = __str__

    @property
    def file_class(self):
        raise NotImplemented('`file_class` must be specified')

    @property
    def model(self):
        raise NotImplemented('`model` must be specified')

    model_dependencies = []
    modifiers = []


class GeonameFeatureImportOptions(ImportOptions):
    file_class = reader.GeonameFeatureReader
    model = models.GeonameFeature


class GeonameTimezoneImportOptions(ImportOptions):
    file_class = reader.GeonameTimezoneReader
    model = models.GeonameTimezone


class GeonameCountryImportOptions(ImportOptions):
    file_class = reader.GeonameCountryInfoReader
    model = models.GeonameCountry


class GeonameImportOptions(ImportOptions):
    file_class = reader.GeonameReader
    model = models.Geoname
    modifiers = [set_geopoint_modifier, clear_empty_fks_modifier]
    model_dependencies = [models.GeonameFeature, models.GeonameTimezone,
                          models.GeonameCountry]


# class GeonameLanguageImportOptions(ImportOptions):
#     file_class = reader.GeonameIsoLanguageCodesReader
#     model = models.GeonameLanguageCode


# class GeonameHierarchyImportOptions(ImportOptions):
#     file_class = reader.GeonameHierarchyReader
#     model = models.GeonameReader


# class GeonameUserTagImportOptions(ImportOptions):
#     file_class = reader.GeonameUserTagsReader
#     model = models.GeonameUserTag


# class GeonameAlternateNameImportOptions(ImportOptions):
#     file_class = reader.GeonameAlternateNamesReader
#     model = models.GeonameAlternateName


_import_options_map = {
    'featureCodes_bg.txt': GeonameFeatureImportOptions,
    'featureCodes_en.txt': GeonameFeatureImportOptions,
    'featureCodes_nb.txt': GeonameFeatureImportOptions,
    'featureCodes_nn.txt': GeonameFeatureImportOptions,
    'featureCodes_no.txt': GeonameFeatureImportOptions,
    'featureCodes_ru.txt': GeonameFeatureImportOptions,
    'featureCodes_sv.txt': GeonameFeatureImportOptions,
    'timeZones.txt': GeonameTimezoneImportOptions,
    'countryInfo.txt': GeonameCountryImportOptions,
    'allCountries.txt': GeonameImportOptions,
    'cities1000.txt': GeonameImportOptions,
    'cities5000.txt': GeonameImportOptions,
    'cities15000.txt': GeonameImportOptions,
    # 'iso-languagecodes.txt': GeonameLanguageImportOptions,
    # 'userTags.txt': GeonameUserTagImportOptions,
    # 'hierarchy.txt': GeonameHierarchyImportOptions,
    # 'alternateNames.txt': GeonameAlternateNameImportOptions,
}


def get_importer_instances(db_session, *filepaths):
    """Creates importer instances from `filepaths` and sorts them by their
    dependencies.
    """
    importer_instances = []
    errmsg = u'No importer defined for filename "{}"'
    for filepath in filepaths:
        filename = _get_import_filename(filepath)
        try:
            importer_options = _import_options_map[filename]
        except KeyError:
            raise Exception(errmsg.format(filename))
        importer_instance = Importer(importer_options, filepath, db_session)
        importer_instances.append(importer_instance)
    return sorted(importer_instances)
